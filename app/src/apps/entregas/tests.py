from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase

from apps.comedores import services as comedor_services
from apps.deposito import services as deposito_services
from apps.entregas import services as entrega_services
from apps.entregas.models import DetalleEntrega, Entrega


class EntregasServicesTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="referente1")
        self.producto = deposito_services.crear_producto(nombre="Arroz")
        self.lote1 = deposito_services.crear_lote(
            numero_lote="L-001",
            fecha_vencimiento=date(2027, 1, 15),
            stock=20,
            nombre_voluntario="Juan",
            producto_id=self.producto.id,
        )
        self.lote2 = deposito_services.crear_lote(
            numero_lote="L-002",
            fecha_vencimiento=date(2027, 3, 15),
            stock=10,
            nombre_voluntario="Juan",
            producto_id=self.producto.id,
        )
        self.comedor = comedor_services.crear_comedor(
            nombre="Comedor Esperanza",
            codigo="CP-001",
            direccion="Calle Falsa 123",
            usuario_id=self.user.id,
        )
        self.entrega = entrega_services.crear_entrega(
            fecha=date(2026, 11, 14),
            nombre_voluntario="Ana",
            comedor_id=self.comedor.id,
            detalles=[
                {"lote_id": self.lote1.id, "cantidad": 6},
                {"lote_id": self.lote2.id, "cantidad": 4},
            ],
        )

    def test_crud_entrega_post(self):
        # POST
        self.assertEqual(self.entrega.estado, Entrega.Estado.REGISTRADA)
        self.assertEqual(len(self.entrega.detalles), 2)

    def test_crud_entrega_get(self):
        # GET
        obtenido = entrega_services.obtener_entrega(self.entrega.id)
        self.assertEqual(obtenido.nombre_voluntario, "Ana")
        self.assertEqual(len(obtenido.detalles), 2)
        self.assertEqual(
                    len(entrega_services.listar_entregas(
                        comedor_id=self.comedor.id, estado=Entrega.Estado.REGISTRADA
                    )),
                    1,
                )

    def test_crear_entrega_descuenta_stock(self):
        self.assertEqual(deposito_services.obtener_lote(self.lote1.id).stock, 14)
        self.assertEqual(deposito_services.obtener_lote(self.lote2.id).stock, 6)

    def test_crear_entrega_es_atomica_si_falla_un_detalle(self):
        with self.assertRaises(ValidationError):
            entrega_services.crear_entrega(
                fecha=date(2026, 11, 14),
                nombre_voluntario="Ana",
                comedor_id=self.comedor.id,
                detalles=[
                    {"lote_id": self.lote1.id, "cantidad": 5},
                    {"lote_id": self.lote2.id, "cantidad": 999},
                ],
            )
        self.assertEqual(len(entrega_services.listar_entregas()), 0)
        self.assertEqual(deposito_services.obtener_lote(self.lote1.id).stock, 20)
        self.assertEqual(deposito_services.obtener_lote(self.lote2.id).stock, 10)

    def test_confirmar_y_anular_entrega(self):
        entrega = entrega_services.crear_entrega(
            fecha=date(2026, 11, 14),
            nombre_voluntario="Ana",
            comedor_id=self.comedor.id,
            detalles=[{"lote_id": self.lote1.id, "cantidad": 8}],
        )
        confirmada = entrega_services.actualizar_entrega(
            entrega.id, estado=Entrega.Estado.CONFIRMADA
        )
        self.assertEqual(confirmada.estado, Entrega.Estado.CONFIRMADA)
        self.assertIsNotNone(confirmada.fecha_confirmacion)
        self.assertEqual(deposito_services.obtener_lote(self.lote1.id).stock, 12)

        anulada = entrega_services.actualizar_entrega(
            entrega.id, estado=Entrega.Estado.ANULADA
        )
        self.assertEqual(anulada.estado, Entrega.Estado.ANULADA)
        self.assertEqual(deposito_services.obtener_lote(self.lote1.id).stock, 20)

        with self.assertRaises(ValidationError):
            entrega_services.actualizar_entrega(
                entrega.id, estado=Entrega.Estado.CONFIRMADA
            )

    def test_eliminar_entrega_restituye_stock_solo_si_no_estaba_anulada(self):
        e1 = entrega_services.crear_entrega(
            fecha=date(2026, 11, 14),
            nombre_voluntario="Ana",
            comedor_id=self.comedor.id,
            detalles=[{"lote_id": self.lote1.id, "cantidad": 5}],
        )
        entrega_services.eliminar_entrega(e1.id)
        self.assertEqual(deposito_services.obtener_lote(self.lote1.id).stock, 20)

        e2 = entrega_services.crear_entrega(
            fecha=date(2026, 11, 14),
            nombre_voluntario="Ana",
            comedor_id=self.comedor.id,
            detalles=[{"lote_id": self.lote1.id, "cantidad": 5}],
        )
        entrega_services.actualizar_entrega(e2.id, estado=Entrega.Estado.ANULADA)
        entrega_services.eliminar_entrega(e2.id)
        self.assertEqual(deposito_services.obtener_lote(self.lote1.id).stock, 20)

    def test_crud_detalle_entrega_y_reajuste_de_stock(self):
        entrega = entrega_services.crear_entrega(
            fecha=date(2026, 11, 14),
            nombre_voluntario="Ana",
            comedor_id=self.comedor.id,
        )
        # POST detalle
        detalle = entrega_services.crear_detalle_entrega(
            entrega_id=entrega.id,
            lote_id=self.lote1.id,
            cantidad=4,
        )
        self.assertEqual(deposito_services.obtener_lote(self.lote1.id).stock, 16)
        self.assertEqual(
            len(entrega_services.listar_detalles_entrega(entrega_id=entrega.id)), 1
        )

        # PUT detalle (cambia lote y cantidad)
        actualizado = entrega_services.actualizar_detalle_entrega(
            detalle.id,
            lote_id=self.lote2.id,
            cantidad=3,
        )
        self.assertEqual(actualizado.lote_id, self.lote2.id)
        self.assertEqual(actualizado.cantidad, 3)
        self.assertEqual(deposito_services.obtener_lote(self.lote1.id).stock, 20)
        self.assertEqual(deposito_services.obtener_lote(self.lote2.id).stock, 7)

        # No permite eliminar lote referenciado
        with self.assertRaises(ProtectedError):
            deposito_services.eliminar_lote(self.lote2.id)

        # DELETE detalle
        entrega_services.eliminar_detalle_entrega(detalle.id)
        self.assertEqual(deposito_services.obtener_lote(self.lote2.id).stock, 10)
        with self.assertRaises(DetalleEntrega.DoesNotExist):
            entrega_services.obtener_detalle_entrega(detalle.id)
