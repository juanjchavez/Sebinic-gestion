"""Pruebas de Usuario y del inicio de sesión con correo (ACC-03, ACC-05)."""

import io

import pytest
from django.contrib.admin.models import LogEntry
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, connection, transaction

from apps.personas.models import Usuario

# Debe coincidir con la contraseña de la fixture `usuario` (conftest.py).
CLAVE_PRUEBA = 'clave-de-prueba-123'


@pytest.mark.django_db
@pytest.mark.regla('ACC-05')
def test_inicia_sesion_con_correo_sin_importar_mayusculas(client, usuario):
    primero = authenticate(email='Ana@x.org', password=CLAVE_PRUEBA)
    segundo = authenticate(email='ana@x.org', password=CLAVE_PRUEBA)
    assert primero is not None and segundo is not None
    assert primero.pk == segundo.pk == usuario.pk
    assert client.login(email='ANA@X.ORG', password=CLAVE_PRUEBA) is True


@pytest.mark.django_db
@pytest.mark.regla('ACC-05')
def test_correo_se_guarda_en_minusculas(usuario):
    usuario.refresh_from_db()
    assert usuario.email == 'ana@x.org'


@pytest.mark.django_db
@pytest.mark.regla('ACC-05')
def test_correo_duplicado_con_otras_mayusculas_se_rechaza(usuario):
    with pytest.raises(ValidationError) as exc:
        Usuario(email='ANA@x.org').full_clean(exclude=['password'])
    assert 'email' in exc.value.message_dict

    with pytest.raises(ValidationError):
        Usuario.objects.create_user(email='ANA@X.ORG', password='x')


@pytest.mark.django_db
@pytest.mark.regla('ACC-05')
def test_constraint_bd_correo_sin_mayusculas(usuario):
    otro = Usuario.objects.create_user(email='otra@x.org', password='x')
    # update() no pasa por save(), así que solo la constraint Lower('email') puede frenarlo.
    with pytest.raises(IntegrityError), transaction.atomic():
        Usuario.objects.filter(pk=otro.pk).update(email='ANA@x.org')


@pytest.mark.django_db
@pytest.mark.regla('ACC-05')
def test_createsuperuser_pide_correo_y_contrasena(monkeypatch):
    assert Usuario.USERNAME_FIELD == 'email'
    assert Usuario.REQUIRED_FIELDS == []

    monkeypatch.setenv('DJANGO_SUPERUSER_PASSWORD', 'clave-admin-123')
    call_command(
        'createsuperuser',
        interactive=False,
        email='Admin@Seminario.org',
        stdout=io.StringIO(),
    )

    admin = Usuario.objects.get(email='admin@seminario.org')
    assert admin.is_superuser and admin.is_staff
    assert admin.persona is None
    assert admin.check_password('clave-admin-123')


@pytest.mark.django_db
@pytest.mark.regla('ACC-03')
def test_una_persona_tiene_un_solo_usuario(usuario, persona_natural):
    with pytest.raises(ValidationError) as exc:
        Usuario(email='otra@x.org', persona=persona_natural).full_clean(exclude=['password'])
    assert 'persona' in exc.value.message_dict


@pytest.mark.django_db
@pytest.mark.regla('ACC-03')
def test_persona_juridica_no_puede_tener_usuario(persona_juridica):
    with pytest.raises(ValidationError) as exc:
        Usuario(email='iglesia@x.org', persona=persona_juridica).full_clean(exclude=['password'])
    assert 'persona' in exc.value.message_dict

    with pytest.raises(ValidationError):
        Usuario.objects.create_user(
            email='iglesia@x.org',
            password='x',
            persona=persona_juridica,
        )


@pytest.mark.django_db
@pytest.mark.regla('ACC-05')
def test_telefono_no_es_credencial(usuario, persona_natural):
    persona_natural.telefono = '88887777'
    persona_natural.save()

    assert authenticate(email='88887777', password=CLAVE_PRUEBA) is None
    entrada = authenticate(email='ana@x.org', password=CLAVE_PRUEBA)
    assert entrada is not None and entrada.pk == usuario.pk


@pytest.mark.django_db
@pytest.mark.regla('ACC-05')
def test_usuario_del_proyecto_reemplaza_auth_user():
    assert get_user_model() is Usuario
    assert 'auth_user' not in connection.introspection.table_names()
    assert LogEntry._meta.get_field('user').related_model is Usuario
