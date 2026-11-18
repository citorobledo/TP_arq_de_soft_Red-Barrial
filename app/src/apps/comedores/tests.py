import json
from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase

from apps.comedores import services as comedor_services
from apps.comedores.models import Comedor
from apps.entregas import services as entrega_services
from apps.seguridad.roles import REFERENTE_COMEDOR


class ComedoresServicesTests(TestCase):

    def setUp(self):
        User = get_user_model()
        grupo_referente, _ = Group.objects.get_or_create(name=REFERENTE_COMEDOR)
        self.user1 = User.objects.create_user(username="referente1")
        self.user1.groups.add(grupo_referente)
        self.user2 = User.objects.create_user(username="referente2")
        self.user2.groups.add(grupo_referente)
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

    def test_no_permite_usuario_sin_rol_referente(self):
        User = get_user_model()
        sin_rol = User.objects.create_user(username="sin_rol")
        with self.assertRaises(ValidationError):
            comedor_services.crear_comedor(
                nombre="Comedor Sin Rol",
                codigo="CP-099",
                direccion="Calle 99",
                usuario_id=sin_rol.id,
            )
        with self.assertRaises(ValidationError):
            comedor_services.actualizar_comedor(
                self.comedor.id,
                usuario_id=sin_rol.id,
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
    def test_sincronizar_solo_actualiza_estado_de_codigos_locales_coincidentes(
        self, mock_urlopen
    ):
        comedor_sin_cambios = comedor_services.crear_comedor(
            nombre="Comedor sin cambios",
            codigo="CP-002",
            direccion="Calle 2",
            usuario_id=self.user2.id,
        )
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = json.dumps(
            [
                {
                    "codigo": "CP-001",
                    "nombre": "Nombre que no debe copiarse",
                    "direccion": "Dirección que no debe copiarse",
                    "usuario_id": 999,
                    "habilitado": False,
                },
                {"codigo": "CP-002", "habilitado": True},
                {"codigo": "CP-NUEVO", "habilitado": False},
            ]
        ).encode()

        resultado = comedor_services.sincronizar_comedores_padron()

        self.assertEqual(
            resultado,
            {"actualizados": 1, "sin_cambios": 1, "sin_coincidencia": 1},
        )
        comedor_local = Comedor.objects.get(pk=self.comedor.id)
        self.assertFalse(comedor_local.habilitado)
        self.assertEqual(comedor_local.nombre, "Comedor Sol")
        self.assertEqual(comedor_local.direccion, "Av. Siempreviva 742")
        self.assertEqual(comedor_local.usuario_id, self.user1.id)
        local_sin_cambios = Comedor.objects.get(pk=comedor_sin_cambios.id)
        self.assertTrue(local_sin_cambios.habilitado)
        self.assertEqual(local_sin_cambios.nombre, "Comedor sin cambios")
        self.assertEqual(local_sin_cambios.direccion, "Calle 2")
        self.assertEqual(local_sin_cambios.usuario_id, self.user2.id)
        self.assertEqual(Comedor.objects.count(), 2)

        response.read.return_value = json.dumps(
            [
                {
                    "codigo": "CP-001",
                    "nombre": "Otro nombre ignorado",
                    "direccion": "Otra dirección ignorada",
                    "habilitado": True,
                },
                {"codigo": "CP-002", "habilitado": True},
                {"codigo": "CP-NUEVO", "habilitado": False},
            ]
        ).encode()

        resultado = comedor_services.sincronizar_comedores_padron()

        self.assertEqual(
            resultado,
            {"actualizados": 1, "sin_cambios": 1, "sin_coincidencia": 1},
        )
        comedor_local.refresh_from_db()
        self.assertTrue(comedor_local.habilitado)
        self.assertEqual(comedor_local.nombre, "Comedor Sol")
        self.assertEqual(comedor_local.direccion, "Av. Siempreviva 742")
        self.assertEqual(comedor_local.usuario_id, self.user1.id)
        local_sin_cambios.refresh_from_db()
        self.assertTrue(local_sin_cambios.habilitado)
        self.assertEqual(Comedor.objects.count(), 2)
