from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from apps.comedores import services as comedor_services
from apps.comedores.models import Comedor
from apps.deposito import services as deposito_services
from apps.entregas import services as entrega_services
from apps.entregas.models import DetalleEntrega, Entrega
from apps.seguridad.roles import REFERENTE_COMEDOR
from apps.seguridad.roles import VOLUNTARIO_DEPOSITO

from . import services

class EntregasServicesTests(TestCase):
    def setUp(self):
        User = get_user_model()
        grupo_referente, _ = Group.objects.get_or_create(name=REFERENTE_COMEDOR)
        self.user = User.objects.create_user(username="referente1")
        self.user.groups.add(grupo_referente)
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
        self.assertEqual(obtenido.comedor_codigo, "CP-001")
        self.assertEqual(obtenido.comedor_nombre, "Comedor Esperanza")
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
        self.assertEqual(len(entrega_services.listar_entregas()), 1)
        self.assertEqual(deposito_services.obtener_lote(self.lote1.id).stock, 14)
        self.assertEqual(deposito_services.obtener_lote(self.lote2.id).stock, 6)

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
        self.assertEqual(deposito_services.obtener_lote(self.lote1.id).stock, 6)

        anulada = entrega_services.actualizar_entrega(
            entrega.id, estado=Entrega.Estado.ANULADA
        )
        self.assertEqual(anulada.estado, Entrega.Estado.ANULADA)
        self.assertEqual(deposito_services.obtener_lote(self.lote1.id).stock, 14)

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
        self.assertEqual(deposito_services.obtener_lote(self.lote1.id).stock, 14)

        e2 = entrega_services.crear_entrega(
            fecha=date(2026, 11, 14),
            nombre_voluntario="Ana",
            comedor_id=self.comedor.id,
            detalles=[{"lote_id": self.lote1.id, "cantidad": 5}],
        )
        entrega_services.actualizar_entrega(e2.id, estado=Entrega.Estado.ANULADA)
        entrega_services.eliminar_entrega(e2.id)
        self.assertEqual(deposito_services.obtener_lote(self.lote1.id).stock, 14)

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
        self.assertEqual(deposito_services.obtener_lote(self.lote1.id).stock, 10)
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
        self.assertEqual(deposito_services.obtener_lote(self.lote1.id).stock, 14)
        self.assertEqual(deposito_services.obtener_lote(self.lote2.id).stock, 3)

        # No permite eliminar lote referenciado
        with self.assertRaises(ProtectedError):
            deposito_services.eliminar_lote(self.lote2.id)

        # DELETE detalle
        entrega_services.eliminar_detalle_entrega(detalle.id)
        self.assertEqual(deposito_services.obtener_lote(self.lote2.id).stock, 6)
        with self.assertRaises(DetalleEntrega.DoesNotExist):
            entrega_services.obtener_detalle_entrega(detalle.id)

class ConfirmarRecepcionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        grupo_referente, _ = Group.objects.get_or_create(name=REFERENTE_COMEDOR)
        self.referente = User.objects.create_user("ana", password="x")
        self.referente.groups.add(grupo_referente)
        self.otro = User.objects.create_user("otro", password="x")
        self.comedor = comedor_services.crear_comedor(
            nombre="Los Pibes",
            codigo="CP-001",
            direccion="Calle 1",
            usuario_id=self.referente.id,
        )
        self.entrega = services.crear_entrega(
            fecha=date.today(), nombre_voluntario="Miriam", comedor_id=self.comedor.id
        )

    def _confirmar(self, usuario=None, nombre="Ana Pérez"):
        usuario = usuario or self.referente
        return services.confirmar_recepcion(
            self.entrega.id, usuario_id=usuario.id, nombre_referente=nombre
        )

    def test_confirma_y_registra_fecha_y_referente(self):
        entrega = self._confirmar()
        self.assertEqual(entrega.estado, Entrega.Estado.CONFIRMADA)
        self.assertIsNotNone(entrega.fecha_confirmacion)
        self.assertEqual(entrega.nombre_referente, "Ana Pérez")

    def test_no_pisa_el_nombre_del_voluntario(self):
        entrega = self._confirmar()
        self.assertEqual(entrega.nombre_voluntario, "Miriam")

    def test_es_idempotente(self):
        primera = self._confirmar(nombre="Ana Pérez")
        segunda = self._confirmar(nombre="Otro Nombre")
        self.assertEqual(segunda.fecha_confirmacion, primera.fecha_confirmacion)
        self.assertEqual(segunda.nombre_referente, "Ana Pérez")

    def test_rechaza_a_un_referente_de_otro_comedor(self):
        with self.assertRaises(ValidationError):
            self._confirmar(usuario=self.otro)
        actual = services.obtener_entrega(self.entrega.id)
        self.assertEqual(actual.estado, Entrega.Estado.REGISTRADA)
        self.assertIsNone(actual.fecha_confirmacion)

    def test_rechaza_una_entrega_anulada(self):
        services.actualizar_entrega(self.entrega.id, estado=Entrega.Estado.ANULADA)
        with self.assertRaises(ValidationError):
            self._confirmar()
        actual = services.obtener_entrega(self.entrega.id)
        self.assertEqual(actual.estado, Entrega.Estado.ANULADA)

    def test_rechaza_nombre_vacio(self):
        with self.assertRaises(ValidationError):
            self._confirmar(nombre="   ")
        actual = services.obtener_entrega(self.entrega.id)
        self.assertEqual(actual.estado, Entrega.Estado.REGISTRADA)

class NuevaEntregaComedoresHabilitadosTests(TestCase):
    def setUp(self):
        User = get_user_model()
        usuario = User.objects.create_user(username="voluntario")
        usuario.groups.add(Group.objects.create(name=VOLUNTARIO_DEPOSITO))
        self.client.force_login(usuario)

        self.producto = deposito_services.crear_producto(nombre="Arroz habilitados")
        self.lote = deposito_services.crear_lote(
            numero_lote="L-HABILITADOS",
            fecha_vencimiento=date(2027, 1, 15),
            stock=20,
            nombre_voluntario="Juan",
            producto_id=self.producto.id,
        )
        self.comedor_habilitado = Comedor.objects.create(
            nombre="Comedor habilitado",
            codigo="CP-HAB",
            direccion="Calle 1",
            habilitado=True,
        )
        self.comedor_no_habilitado = Comedor.objects.create(
            nombre="Comedor no habilitado",
            codigo="CP-DESHAB",
            direccion="Calle 2",
            habilitado=False,
        )

    def test_desplegable_muestra_solo_comedores_habilitados(self):
        response = self.client.get(reverse("nueva_entrega"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'value="{self.comedor_habilitado.id}"')
        self.assertNotContains(response, f'value="{self.comedor_no_habilitado.id}"')
        self.assertContains(response, 'id="nombre_voluntario"')
        self.assertContains(response, "readonly")

    def test_rechaza_post_para_comedor_no_habilitado(self):
        response = self.client.post(
            reverse("nueva_entrega"),
            {
                "comedor": self.comedor_no_habilitado.id,
                "lote_id": [self.lote.id],
                "cantidad": ["2"],
                "fecha": date.today().isoformat(),
                "nombre_voluntario": "Juan",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "No se pueden registrar entregas para un comedor no habilitado."
        )
        self.assertEqual(Entrega.objects.count(), 0)
        self.assertEqual(deposito_services.obtener_lote(self.lote.id).stock, 20)

    def test_nombre_voluntario_se_toma_del_usuario_autenticado(self):
        response = self.client.post(
            reverse("nueva_entrega"),
            {
                "comedor": self.comedor_habilitado.id,
                "lote_id": [self.lote.id],
                "cantidad": ["2"],
                "fecha": date.today().isoformat(),
                "nombre_voluntario": "Nombre manipulado",
            },
        )

        self.assertRedirects(response, reverse("entregas"))
        entrega = Entrega.objects.get()
        self.assertEqual(entrega.nombre_voluntario, "voluntario")
