"""Semilla real e idempotencia de roles (ACC-03/04, sección 3)."""

from io import StringIO

import pytest
from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command

from apps.personas.roles import ALUMNO, MAESTRO, PERMISOS_INICIALES, ROLES
from apps.personas.signals import crear_roles

pytestmark = [pytest.mark.django_db, pytest.mark.regla('ACC-03', 'ACC-04', 'Sección 3')]


def sembrar():
    crear_roles(apps.get_app_config('personas'), apps=apps, using='default')


def test_instalacion_crea_solo_cuatro_grupos_con_permisos_exactos():
    assert set(Group.objects.values_list('name', flat=True)) == set(ROLES)
    for nombre, codigos in PERMISOS_INICIALES.items():
        permisos = Group.objects.get(name=nombre).permissions
        assert set(permisos.values_list('codename', flat=True)) == set(codigos)
        assert not permisos.exclude(
            content_type__app_label='personas', content_type__model='persona',
        ).exists()


def test_repetir_migrate_conserva_identidad_y_personalizaciones():
    originales = dict(Group.objects.values_list('name', 'pk'))
    grupo = Group.objects.get(name=ROLES[0])
    grupo.permissions.clear()
    alumno = Group.objects.get(name=ALUMNO)
    permiso = Permission.objects.get(content_type__app_label='personas', codename='view_persona')
    alumno.permissions.add(permiso)
    ajeno = Group.objects.create(name='Grupo ajeno')
    for _ in range(2):
        call_command('migrate', interactive=False, verbosity=0, stdout=StringIO())
    assert dict(Group.objects.filter(name__in=ROLES).values_list('name', 'pk')) == originales
    assert not grupo.permissions.exists()
    assert list(alumno.permissions.all()) == [permiso]
    assert Group.objects.filter(pk=ajeno.pk).exists()


def test_solo_grupos_nuevos_reciben_permisos():
    Group.objects.get(name=ROLES[0]).permissions.clear()
    Group.objects.filter(name=ROLES[1]).delete()
    sembrar()
    assert not Group.objects.get(name=ROLES[0]).permissions.exists()
    assert Group.objects.get(name=ROLES[1]).permissions.count() == 3


def test_permiso_faltante_revierte_semilla_completa():
    Group.objects.all().delete()
    Permission.objects.filter(content_type__app_label='personas', codename='view_persona').delete()
    with pytest.raises(ImproperlyConfigured, match='view_persona'):
        sembrar()
    assert not Group.objects.exists()


def test_renombrado_no_transfiere_miembros(usuario):
    grupo = Group.objects.get(name=MAESTRO)
    usuario.groups.add(grupo)
    grupo.name = 'Maestro renombrado'
    grupo.save()
    sembrar()
    assert usuario.groups.get() == grupo
    assert not Group.objects.get(name=MAESTRO).user_set.exists()


def test_ready_repetido_no_duplica_receptor():
    from django.db.models.signals import post_migrate

    configuracion = apps.get_app_config('personas')
    configuracion.ready()
    configuracion.ready()
    respuestas = post_migrate.send(sender=configuracion, app_config=configuracion,
                                   apps=apps, using='default', verbosity=0, interactive=False)
    assert sum(receptor is crear_roles for receptor, _ in respuestas) == 1


@pytest.mark.django_db(transaction=True)
def test_flush_recrea_roles_mediante_senal_real():
    # Solo BD de pruebas: flush emite post_migrate con el registro global.
    call_command('flush', interactive=False, verbosity=0, stdout=StringIO())
    test_instalacion_crea_solo_cuatro_grupos_con_permisos_exactos()
