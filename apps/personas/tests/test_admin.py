"""Frontera HTTP del panel y campos efectivos (ACC-03/04/05, C39)."""

from unittest.mock import patch

import pytest
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.personas.models import Usuario
from apps.personas.roles import ROLES

pytestmark = [pytest.mark.django_db, pytest.mark.regla('ACC-03', 'ACC-04', 'Sección 3', 'C39')]


@pytest.fixture
def administrador():
    return Usuario.objects.create_superuser(email='admin@seminario.org')


@pytest.fixture
def cliente_admin(client, administrador):
    client.force_login(administrador)
    return client


@pytest.mark.regla('ACC-05')
def test_administrador_inicia_sesion_por_correo(client, administrador):
    administrador.set_password('clave-segura-de-prueba')
    administrador.save(update_fields=['password'])
    respuesta = client.post(reverse('admin:login'), {
        'username': administrador.email, 'password': 'clave-segura-de-prueba',
        'next': reverse('admin:index'),
    })
    assert respuesta.status_code == 302
    assert client.get(reverse('admin:index')).status_code == 200


@pytest.mark.parametrize('rol', ROLES + ('todos', 'staff'))
@pytest.mark.parametrize('modelo', ['personas_persona', 'personas_usuario', 'auth_group'])
def test_usuarios_operativos_no_entran_a_endpoints(client, usuario, rol, modelo):
    grupos = Group.objects.filter(name__in=ROLES if rol == 'todos' else [rol])
    usuario.groups.add(*grupos)
    usuario.is_staff = True
    usuario.save(update_fields=['is_staff'])
    usuario.user_permissions.add(*Permission.objects.all())
    client.force_login(usuario)
    objeto_id = {
        'personas_persona': usuario.persona_id,
        'personas_usuario': usuario.pk,
        'auth_group': Group.objects.first().pk,
    }[modelo]
    for url in (
        reverse(f'admin:{modelo}_changelist'),
        reverse(f'admin:{modelo}_change', args=[objeto_id]),
    ):
        for respuesta in (client.get(url), client.post(url, {})):
            assert respuesta.status_code == 302
            assert reverse('admin:login') in respuesta.url
    assert client.post(reverse('admin:login'), {
        'username': usuario.email, 'password': 'clave-de-prueba-123',
    }).status_code == 200


def test_superusuario_inactivo_no_entra(client, administrador):
    # Crear directamente inactivo no degrada un Administrador que ya existía.
    inactivo = Usuario.objects.create_superuser(email='inactivo@seminario.org', is_active=False)
    client.force_login(inactivo)
    assert client.get(reverse('admin:index')).status_code == 302


def test_administrador_edita_permisos_de_grupos(cliente_admin):
    grupo = Group.objects.get(name=ROLES[0])
    permiso = Permission.objects.get(content_type__app_label='personas', codename='view_persona')
    respuesta = cliente_admin.post(reverse('admin:auth_group_change', args=[grupo.pk]), {
        'name': grupo.name, 'permissions': [permiso.pk], '_save': 'Guardar',
    })
    assert respuesta.status_code == 302
    assert list(grupo.permissions.all()) == [permiso]


def datos_persona(persona):
    return {
        'tipo': persona.tipo, 'nombres': persona.nombres, 'apellidos': persona.apellidos,
        'tipo_identificacion': persona.tipo_identificacion,
        'numero_identificacion': persona.numero_identificacion,
        'correo': 'cambiado@seminario.org', 'telefono': '1234', 'direccion': '',
        '_save': 'Guardar',
    }


@pytest.mark.regla('ACC-05', 'TEC-07')
@pytest.mark.parametrize('con_usuario', [True, False])
def test_correo_persona_protegido_y_auditoria(cliente_admin, administrador, persona_natural, con_usuario):
    if con_usuario:
        Usuario.objects.create_user(email=persona_natural.correo, persona=persona_natural)
    original = persona_natural.correo
    url = reverse('admin:personas_persona_change', args=[persona_natural.pk])
    formulario = cliente_admin.get(url).context['adminform'].form
    assert ('correo' not in formulario.fields) is con_usuario
    respuesta = cliente_admin.post(url, datos_persona(persona_natural))
    assert respuesta.status_code == 302
    persona_natural.refresh_from_db()
    assert persona_natural.correo == (original if con_usuario else 'cambiado@seminario.org')
    assert persona_natural.historial.first().history_user == administrador


def test_post_no_cambia_credenciales_roles_ni_persona(cliente_admin, usuario, persona_juridica):
    url = reverse('admin:personas_usuario_change', args=[usuario.pk])
    correo, clave, persona = usuario.email, usuario.password, usuario.persona_id
    formulario = cliente_admin.get(url).context['adminform'].form
    assert set(formulario.fields) == {'is_active', 'is_staff', 'is_superuser'}
    respuesta = cliente_admin.post(url, {
        'is_active': 'on', 'email': 'intruso@seminario.org', 'password': 'texto',
        'persona': persona_juridica.pk,
        'groups': [Group.objects.get(name=ROLES[0]).pk],
        'user_permissions': [Permission.objects.first().pk], '_save': 'Guardar',
    })
    assert respuesta.status_code == 302
    usuario.refresh_from_db()
    assert (usuario.email, usuario.password, usuario.persona_id) == (correo, clave, persona)
    assert not usuario.groups.exists()
    assert not usuario.user_permissions.exists()


def test_altas_y_bajas_de_usuario_bloqueadas(cliente_admin, usuario):
    for accion, args in [('add', []), ('delete', [usuario.pk])]:
        url = reverse(f'admin:personas_usuario_{accion}', args=args)
        assert cliente_admin.get(url).status_code == 403
        assert cliente_admin.post(url, {'post': 'yes'}).status_code == 403
    respuesta = cliente_admin.post(reverse('admin:personas_usuario_changelist'), {
        'action': 'delete_selected', '_selected_action': [usuario.pk], 'post': 'yes',
    })
    assert respuesta.status_code == 200
    assert Usuario.objects.filter(pk=usuario.pk).exists()


def test_ultimo_administrador_recibe_error_de_formulario(cliente_admin, administrador):
    respuesta = cliente_admin.post(reverse('admin:personas_usuario_change', args=[administrador.pk]), {
        'is_staff': 'on', 'is_superuser': 'on', '_save': 'Guardar',
    })
    assert respuesta.status_code == 200
    assert 'Administrador activo' in str(respuesta.context['adminform'].form.errors)
    administrador.refresh_from_db()
    assert administrador.is_active


def test_rechazo_concurrente_no_devuelve_500(cliente_admin, usuario):
    antes = usuario.historial.count()
    url = reverse('admin:personas_usuario_change', args=[usuario.pk])
    with patch.object(Usuario, 'save', side_effect=ValidationError('Rechazo concurrente C39')):
        respuesta = cliente_admin.post(url, {'is_active': 'on', '_save': 'Guardar'})
    assert respuesta.status_code == 302
    assert respuesta.url == url
    assert usuario.historial.count() == antes
    assert 'Rechazo concurrente C39' in cliente_admin.get(url).content.decode()
