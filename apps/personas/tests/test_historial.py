"""Pruebas de la auditoría con django-simple-history (TEC-07)."""

import pytest
from django.conf import settings
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.test import RequestFactory
from simple_history.middleware import HistoryRequestMiddleware

from apps.personas.models import Persona, Usuario

CLAVE_PRUEBA = 'clave-de-prueba-123'


@pytest.mark.django_db
@pytest.mark.regla('TEC-07')
def test_historial_registra_autor_en_peticion_con_sesion(usuario, persona_juridica):
    def vista(request):
        persona_juridica.nombres = 'Iglesia Renovada'
        persona_juridica.save()
        return HttpResponse('ok')

    request = RequestFactory().post('/')
    request.user = usuario
    HistoryRequestMiddleware(vista)(request)

    ultimo = persona_juridica.historial.first()
    assert ultimo.history_user == usuario
    assert ultimo.nombres == 'Iglesia Renovada'


@pytest.mark.django_db
@pytest.mark.regla('TEC-07')
def test_historial_sin_autor_fuera_de_peticion(persona_juridica):
    persona_juridica.nombres = 'Iglesia Sin Autor'
    persona_juridica.save()

    ultimo = persona_juridica.historial.first()
    assert ultimo.history_user is None
    assert ultimo.nombres == 'Iglesia Sin Autor'


@pytest.mark.django_db
@pytest.mark.regla('TEC-07')
def test_iniciar_sesion_no_crea_historial(client, usuario):
    antes = usuario.historial.count()

    assert client.login(email='ana@x.org', password=CLAVE_PRUEBA) is True
    usuario.refresh_from_db()

    assert usuario.last_login is not None
    assert usuario.historial.count() == antes


@pytest.mark.django_db
@pytest.mark.regla('TEC-07')
def test_cambio_de_grupos_queda_registrado(usuario):
    grupo = Group.objects.create(name='Prueba')
    antes = usuario.historial.count()

    usuario.groups.add(grupo)

    assert usuario.historial.count() == antes + 1
    assert usuario.historial.first().groups.filter(group=grupo).exists()


@pytest.mark.django_db
@pytest.mark.regla('TEC-07')
def test_historial_de_usuario_excluye_contrasena_y_ultimo_inicio():
    nombres_de_campo = {f.name for f in Usuario.historial.model._meta.get_fields()}

    assert 'password' not in nombres_de_campo
    assert 'last_login' not in nombres_de_campo
    assert 'email' in nombres_de_campo


@pytest.mark.django_db
@pytest.mark.regla('TEC-07')
def test_middleware_de_historial_despues_de_autenticacion():
    middleware = settings.MIDDLEWARE
    indice_historial = middleware.index('simple_history.middleware.HistoryRequestMiddleware')
    indice_autenticacion = middleware.index('django.contrib.auth.middleware.AuthenticationMiddleware')
    assert indice_historial > indice_autenticacion


@pytest.mark.django_db
@pytest.mark.regla('TEC-07')
def test_persona_tiene_historial_completo():
    persona = Persona.objects.create(
        tipo='natural',
        nombres='Marta',
        apellidos='Solís',
        tipo_identificacion='cedula',
        numero_identificacion='001-010101-0001A',
        correo='marta@x.org',
    )

    registros = persona.historial.all()
    assert registros.count() == 1
    assert registros.first().history_type == '+'

    nombres_de_campo = {f.name for f in Persona.historial.model._meta.get_fields()}
    assert {'numero_identificacion', 'correo', 'tipo'} <= nombres_de_campo
