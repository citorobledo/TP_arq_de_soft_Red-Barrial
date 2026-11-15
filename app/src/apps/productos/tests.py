from datetime import date

from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase

from apps.deposito import services as deposito_services
from apps.productos import services as producto_services
from apps.productos.models import Producto


class ProductoServicesTests(TestCase):

    def setUp(self):
        self.prod = producto_services.crear_producto(nombre="  Arroz Largo Fino  ")

    def test_crud_producto_post(self):
        # POST
        
        self.assertEqual(self.prod.nombre, "Arroz Largo Fino")

    def test_crud_producto_get(self):
        # GET
        self.assertEqual(producto_services.obtener_producto(self.prod.id).nombre, "Arroz Largo Fino")
        self.assertEqual(producto_services.listar_productos().count(), 1)
        self.assertEqual(self.prod.to_dict(), {"id": self.prod.id, "nombre": "Arroz Largo Fino"})
        
    def test_crud_producto_put(self):
        # PUT
        actualizado = producto_services.actualizar_producto(self.prod.id, nombre="Arroz Integral")
        self.assertEqual(actualizado.nombre, "Arroz Integral")

    def test_crud_producto_delete(self):
        # DELETE
        producto_services.eliminar_producto(self.prod.id)
        self.assertEqual(producto_services.listar_productos().count(), 0)
        with self.assertRaises(Producto.DoesNotExist):
            producto_services.obtener_producto(self.prod.id)

    def test_no_permite_nombre_duplicado(self):
        producto_services.crear_producto(nombre="Fideos")
        with self.assertRaises(ValidationError):
            producto_services.crear_producto(nombre="Fideos")

    def test_no_permite_eliminar_producto_con_lotes(self):
        prod = producto_services.crear_producto(nombre="Leche")
        deposito_services.crear_lote(
            numero_lote="L-001",
            fecha_vencimiento=date(2027, 6, 1),
            stock=10,
            nombre_voluntario="Juan",
            producto_id=prod.id,
        )
        with self.assertRaises(ProtectedError):
            producto_services.eliminar_producto(prod.id)
