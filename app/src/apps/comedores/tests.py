import json
from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase

from apps.comedores import services as comedor_services
from apps.comedores.models import Comedor
from apps.entregas import services as entrega_services


class ComedoresServicesTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user1 = User.objects.create_user(username="referente1")
        self.user2 = User.objects.create_user(username="referente2")
        self.comedor = comedor_services.crear_comedor(
            nombre="  Comedor Sol  ",
            codigo="  CP-001  ",
            direccion="  Av. Siempreviva 742  ",
            usuario_id=self.user1.id,
        )

    def test_crud_comedor_post(self):
        # POST
        self.assertEqual(self.comedor.nombre, "Comedor Sol")
        self.assertEqual(self.comedor.codigo, "CP-001")
    
    def test_crud_comedor_get(self):
        # GET
        self.assertEqual(comedor_services.obtener_comedor(self.comedor.id).nombre, "Comedor Sol")
        self.assertEqual(comedor_services.obtener_comedor_por_codigo("CP-001").id, self.comedor.id)
        self.assertEqual(len(comedor_services.listar_comedores(usuario_id=self.user1.id)), 1)
        self.assertEqual(len(comedor_services.listar_comedores(usuario_id=self.user2.id)), 0)

    def test_crud_comedor_put(self):
        # PUT
        actualizado = comedor_services.actualizar_comedor(
            self.comedor.id,
            nombre="Comedor Luna",
            usuario_id=self.user2.id,
        )
        self.assertEqual(actualizado.nombre, "Comedor Luna")
        self.assertEqual(actualizado.usuario_id, self.user2.id)

    def test_crud_comedor_delete(self):
        # DELETE
        comedor_services.eliminar_comedor(self.comedor.id)
        with self.assertRaises(Comedor.DoesNotExist):
            comedor_services.obtener_comedor(self.comedor.id)

    def test_no_permite_codigo_duplicado(self):
        comedor_services.crear_comedor(
            nombre="Comedor A",
            codigo="CP-010",
            direccion="Calle 1",
            usuario_id=self.user1.id,
        )
        with self.assertRaises(ValidationError):
            comedor_services.crear_comedor(
                nombre="Comedor B",
                codigo="CP-010",
                direccion="Calle 2",
                usuario_id=self.user2.id,
            )

    def test_no_permite_eliminar_comedor_con_entregas(self):
        comedor = comedor_services.crear_comedor(
            nombre="Comedor A",
            codigo="CP-020",
            direccion="Calle 1",
            usuario_id=self.user1.id,
        )
        entrega_services.crear_entrega(
            fecha=date(2026, 11, 14),
            nombre_voluntario="Ana",
            comedor_id=comedor.id,
        )
        with self.assertRaises(ProtectedError):
            comedor_services.eliminar_comedor(comedor.id)

    @patch("apps.comedores.services.urlopen")
    def test_sincronizar_padron_inserta_y_actualiza_usuario_por_id(
        self, mock_urlopen
    ):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = json.dumps(
            [
                {
                    "codigo": "CP-101",
                    "nombre": "Comedor del padrón",
                    "direccion": "Calle 123",
                    "usuario_id": self.user1.id,
                    "habilitado": True,
                },
                {
                    "codigo": "CP-102",
                    "nombre": "Comedor sin usuario local",
                    "direccion": "Calle 456",
                    "usuario_id": 999,
                    "habilitado": False,
                },
            ]
        ).encode()

        resultado = comedor_services.sincronizar_comedores_padron()

        self.assertEqual(resultado, {"insertados": 2, "actualizados": 0})
        comedor_asignado = Comedor.objects.get(codigo="CP-101")
        self.assertEqual(comedor_asignado.usuario, self.user1)
        self.assertEqual(comedor_asignado.direccion, "Calle 123")
        self.assertTrue(comedor_asignado.habilitado)

        comedor_sin_referente = Comedor.objects.get(codigo="CP-102")
        self.assertIsNone(comedor_sin_referente.usuario_id)
        self.assertEqual(comedor_sin_referente.direccion, "Calle 456")
        self.assertFalse(comedor_sin_referente.habilitado)
        dto = comedor_services.obtener_comedor(comedor_sin_referente.id)
        self.assertEqual(dto.usuario_nombre, "")
        self.assertFalse(dto.habilitado)

        response.read.return_value = json.dumps(
            [
                {
                    "codigo": "CP-101",
                    "nombre": "Comedor actualizado",
                    "direccion": "Calle 789",
                    "usuario_id": self.user2.id,
                    "habilitado": False,
                },
                {
                    "codigo": "CP-102",
                    "nombre": "Comedor sin usuario local",
                    "direccion": "Calle 456",
                    "usuario_id": 999,
                    "habilitado": True,
                },
            ]
        ).encode()

        resultado = comedor_services.sincronizar_comedores_padron()

        self.assertEqual(resultado, {"insertados": 0, "actualizados": 2})
        comedor_asignado.refresh_from_db()
        self.assertEqual(comedor_asignado.nombre, "Comedor actualizado")
        self.assertEqual(comedor_asignado.direccion, "Calle 789")
        self.assertEqual(comedor_asignado.usuario, self.user2)
        self.assertFalse(comedor_asignado.habilitado)
        comedor_sin_referente.refresh_from_db()
        self.assertTrue(comedor_sin_referente.habilitado)
        self.assertEqual(Comedor.objects.filter(codigo__startswith="CP-10").count(), 2)
