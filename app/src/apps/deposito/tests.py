from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase

from apps.deposito import services as deposito_services
from apps.deposito.models import Lote, Producto


class ProductoServicesTests(TestCase):
    def setUp(self):
        self.prod = deposito_services.crear_producto(nombre="  Arroz Largo Fino  ")

    def test_crud_producto(self):
        self.assertEqual(self.prod.nombre, "Arroz Largo Fino")
        self.assertEqual(deposito_services.obtener_producto(self.prod.id).nombre, "Arroz Largo Fino")
        self.assertEqual(len(deposito_services.listar_productos()), 1)

        actualizado = deposito_services.actualizar_producto(self.prod.id, nombre="Arroz Integral")
        self.assertEqual(actualizado.nombre, "Arroz Integral")

        deposito_services.eliminar_producto(self.prod.id)
        self.assertEqual(len(deposito_services.listar_productos()), 0)
        with self.assertRaises(Producto.DoesNotExist):
            deposito_services.obtener_producto(self.prod.id)

    def test_no_permite_nombre_duplicado(self):
        deposito_services.crear_producto(nombre="Fideos")
        with self.assertRaises(ValidationError):
            deposito_services.crear_producto(nombre="Fideos")

    def test_no_permite_eliminar_producto_con_lotes(self):
        deposito_services.crear_lote(
            numero_lote="L-PROT",
            fecha_vencimiento=date(2027, 6, 1),
            stock=10,
            nombre_voluntario="Juan",
            producto_id=self.prod.id,
        )
        with self.assertRaises(ProtectedError):
            deposito_services.eliminar_producto(self.prod.id)


class DepositoServicesTests(TestCase):
    def setUp(self):
        self.arroz = deposito_services.crear_producto(nombre="Arroz")
        self.fideos = deposito_services.crear_producto(nombre="Fideos")
        self.lote = deposito_services.crear_lote(
            numero_lote="  L-001  ",
            fecha_vencimiento=date(2027, 3, 10),
            stock=50,
            nombre_voluntario="  Maria  ",
            nombre_donante="  Supermercado Sol  ",
            producto_id=self.arroz.id,
        )

    def test_crud_lote_post(self):
        # POST
        self.assertEqual(self.lote.numero_lote, "L-001")
        self.assertEqual(self.lote.nombre_voluntario, "Maria")
        self.assertEqual(self.lote.nombre_donante, "Supermercado Sol")
        
    def test_crud_lote_get(self):
        # GET
        obtenido = deposito_services.obtener_lote(self.lote.id)
        self.assertEqual(obtenido.stock, 50)
        self.assertEqual(obtenido.fecha_ingreso, date.today())
        self.assertEqual(obtenido.nombre_producto, "Arroz")
        self.assertEqual(obtenido.nombre_voluntario, "Maria")
        self.assertEqual(obtenido.nombre_donante, "Supermercado Sol")

    def test_crud_lote_put(self):
        # PUT
        nueva_fecha = date(2026, 11, 1)
        actualizado = deposito_services.actualizar_lote(
            self.lote.id,
            stock=60,
            fecha_ingreso=nueva_fecha,
            nombre_voluntario="Pedro",
            nombre_donante="Panadería Sur",
        )
        self.assertEqual(actualizado.stock, 60)
        self.assertEqual(actualizado.fecha_ingreso, nueva_fecha)
        self.assertEqual(actualizado.nombre_voluntario, "Pedro")
        self.assertEqual(actualizado.nombre_donante, "Panadería Sur")

    def test_crud_lote_delete(self):
        # DELETE
        deposito_services.eliminar_lote(self.lote.id)
        with self.assertRaises(Lote.DoesNotExist):
            deposito_services.obtener_lote(self.lote.id)

    def test_listar_lotes_orden_fefo_y_filtros(self):
        lote_lejano = deposito_services.crear_lote(
            numero_lote="L-002",
            fecha_vencimiento=date(2027, 12, 1),
            stock=10,
            nombre_voluntario="Ana",
            producto_id=self.arroz.id,
        )
        lote_cercano = deposito_services.crear_lote(
            numero_lote="L-004",
            fecha_vencimiento=date(2027, 1, 15),
            stock=5,
            nombre_voluntario="Ana",
            producto_id=self.arroz.id,
        )
        deposito_services.crear_lote(
            numero_lote="L-003",
            fecha_vencimiento=date(2027, 2, 1),
            stock=0,
            nombre_voluntario="Ana",
            producto_id=self.fideos.id,
        )

        con_stock = list(deposito_services.listar_lotes(solo_con_stock=True))
        self.assertEqual(
            [l.id for l in con_stock],
            [lote_cercano.id, self.lote.id, lote_lejano.id],
        )

        solo_fideos = list(deposito_services.listar_lotes(producto_id=self.fideos.id))
        self.assertEqual(len(solo_fideos), 1)
        self.assertEqual(solo_fideos[0].numero_lote, "L-003")

    def test_descontar_y_restituir_stock(self):
        lote = deposito_services.crear_lote(
            numero_lote="L-010",
            fecha_vencimiento=date(2027, 5, 1),
            stock=15,
            nombre_voluntario="Luis",
            producto_id=self.arroz.id,
        )
        deposito_services.descontar_stock(lote.id, 6)
        self.assertEqual(deposito_services.obtener_lote(lote.id).stock, 9)

        with self.assertRaises(ValidationError):
            deposito_services.descontar_stock(lote.id, 10)
        self.assertEqual(deposito_services.obtener_lote(lote.id).stock, 9)

        with self.assertRaises(ValidationError):
            deposito_services.descontar_stock(lote.id, 0)

        deposito_services.restituir_stock(lote.id, 4)
        self.assertEqual(deposito_services.obtener_lote(lote.id).stock, 13)

        with self.assertRaises(ValidationError):
            deposito_services.restituir_stock(lote.id, -1)

    def test_no_permite_stock_negativo_al_crear(self):
        with self.assertRaises(ValidationError):
            deposito_services.crear_lote(
                numero_lote="L-NEG",
                fecha_vencimiento=date(2027, 5, 1),
                stock=-5,
                nombre_voluntario="Luis",
                producto_id=self.arroz.id,
            )

    def test_listar_lotes_por_vencer(self):
        hoy = date(2026, 11, 17)
        lote_hoy = deposito_services.crear_lote(
            numero_lote="L-HOY",
            fecha_vencimiento=hoy,
            stock=5,
            nombre_voluntario="Ana",
            producto_id=self.arroz.id,
        )
        lote_en_7d = deposito_services.crear_lote(
            numero_lote="L-7D",
            fecha_vencimiento=hoy + timedelta(days=7),
            stock=3,
            nombre_voluntario="Ana",
            producto_id=self.arroz.id,
        )
        deposito_services.crear_lote(
            numero_lote="L-VENCIDO",
            fecha_vencimiento=hoy - timedelta(days=1),
            stock=4,
            nombre_voluntario="Ana",
            producto_id=self.arroz.id,
        )
        deposito_services.crear_lote(
            numero_lote="L-8D",
            fecha_vencimiento=hoy + timedelta(days=8),
            stock=4,
            nombre_voluntario="Ana",
            producto_id=self.arroz.id,
        )
        deposito_services.crear_lote(
            numero_lote="L-SIN-STOCK",
            fecha_vencimiento=hoy + timedelta(days=2),
            stock=0,
            nombre_voluntario="Ana",
            producto_id=self.arroz.id,
        )

        por_vencer = deposito_services.listar_lotes_por_vencer(dias=7, hoy=hoy)
        self.assertEqual([l.id for l in por_vencer], [lote_hoy.id, lote_en_7d.id])
