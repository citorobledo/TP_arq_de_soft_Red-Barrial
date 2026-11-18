"""Pruebas de seguridad de la API REST: autenticación, roles y campos protegidos."""
import re

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase

from apps.comedores.models import Comedor
from apps.entregas.models import Entrega
from config.api import api

from .roles import COORDINADOR, REFERENTE_COMEDOR, VOLUNTARIO_DEPOSITO


def _usuario(nombre, rol=None, **extra):
    usuario = User.objects.create_user(username=nombre, **extra)
    if rol:
        usuario.groups.add(Group.objects.get_or_create(name=rol)[0])
    return usuario


def _operaciones():
    """Todas las operaciones (método, ruta) declaradas en el esquema OpenAPI."""
    for ruta, metodos in api.get_openapi_schema()["paths"].items():
        for metodo in metodos:
            yield metodo.upper(), re.sub(r"\{[^}]+\}", "1", ruta)


class AutenticacionDeLaApiTests(TestCase):
    def test_hay_operaciones_en_el_esquema(self):
        self.assertGreater(len(list(_operaciones())), 20)

    def test_sin_sesion_toda_operacion_responde_401(self):
        """Falla si alguien agrega un endpoint sin autenticación."""
        cliente = Client()
        for metodo, ruta in _operaciones():
            with self.subTest(operacion=f"{metodo} {ruta}"):
                respuesta = cliente.generic(metodo, ruta, "{}", "application/json")
                self.assertEqual(respuesta.status_code, 401)

    def test_referente_no_puede_usar_la_api(self):
        cliente = Client()
        cliente.force_login(_usuario("ref", REFERENTE_COMEDOR))
        for metodo, ruta in _operaciones():
            with self.subTest(operacion=f"{metodo} {ruta}"):
                respuesta = cliente.generic(metodo, ruta, "{}", "application/json")
                self.assertEqual(respuesta.status_code, 403)

    def test_usuario_sin_rol_no_puede_usar_la_api(self):
        cliente = Client()
        cliente.force_login(_usuario("sinrol"))
        self.assertEqual(cliente.get("/api/comedores/").status_code, 403)

    def test_deposito_y_coordinador_pueden_leer(self):
        for rol in (VOLUNTARIO_DEPOSITO, COORDINADOR):
            with self.subTest(rol=rol):
                cliente = Client()
                cliente.force_login(_usuario(f"u_{rol}", rol))
                self.assertEqual(cliente.get("/api/comedores/").status_code, 200)

    def test_escritura_exige_token_csrf(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(_usuario("dep", VOLUNTARIO_DEPOSITO))
        respuesta = cliente.post("/api/entregas/", {}, content_type="application/json")
        self.assertEqual(respuesta.status_code, 403)


class CamposProtegidosDeEntregasTests(TestCase):
    def setUp(self):
        self.referente = _usuario("ref", REFERENTE_COMEDOR)
        self.comedor = Comedor.objects.create(
            nombre="Comedor Uno", codigo="C1", direccion="Calle 1", usuario=self.referente
        )
        self.entrega = Entrega.objects.create(
            fecha="2026-11-18", nombre_voluntario="Ana", comedor=self.comedor
        )
        self.cliente = Client()
        self.cliente.force_login(
            _usuario("vol", VOLUNTARIO_DEPOSITO, first_name="Vera", last_name="Voluntaria")
        )

    def test_put_no_puede_confirmar_una_entrega(self):
        respuesta = self.cliente.put(
            f"/api/entregas/{self.entrega.id}",
            {"estado": "confirmada", "fecha_confirmacion": "2026-11-18T10:00:00"},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 200)
        self.entrega.refresh_from_db()
        self.assertEqual(self.entrega.estado, Entrega.Estado.REGISTRADA)
        self.assertIsNone(self.entrega.fecha_confirmacion)

    def test_put_no_puede_cambiar_el_nombre_del_voluntario(self):
        self.cliente.put(
            f"/api/entregas/{self.entrega.id}",
            {"nombre_voluntario": "Otra persona"},
            content_type="application/json",
        )
        self.entrega.refresh_from_db()
        self.assertEqual(self.entrega.nombre_voluntario, "Ana")

    def test_el_voluntario_de_una_entrega_nueva_sale_de_la_sesion(self):
        respuesta = self.cliente.post(
            "/api/entregas/",
            {"fecha": "2026-11-18", "comedor_id": self.comedor.id,
             "nombre_voluntario": "Falso", "estado": "confirmada"},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 201)
        cuerpo = respuesta.json()
        self.assertEqual(cuerpo["nombre_voluntario"], "Vera Voluntaria")
        self.assertEqual(cuerpo["estado"], "registrada")
