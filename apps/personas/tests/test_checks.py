from unittest.mock import patch

import pytest
from django.contrib.auth.models import Group
from django.db import OperationalError, connection

from apps.personas.checks import comprobar_roles
from apps.personas.roles import ALUMNO

pytestmark = pytest.mark.regla('Sección 3', 'C39')


def test_sin_alias_no_abre_conexiones():
    # Sin django_db, cualquier apertura real de conexión falla además por pytest-django.
    with patch('apps.personas.checks.connections') as conexiones:
        assert comprobar_roles(databases=None) == []
        conexiones.__getitem__.assert_not_called()


@pytest.mark.django_db
def test_roles_presentes():
    assert comprobar_roles(databases=['default']) == []


@pytest.mark.django_db
@pytest.mark.parametrize('renombrar', [False, True])
def test_grupo_ausente_o_renombrado(renombrar):
    grupo = Group.objects.get(name=ALUMNO)
    if renombrar:
        grupo.name = 'Alumno renombrado'
        grupo.save()
    else:
        grupo.delete()
    avisos = comprobar_roles(databases=['default'])
    assert [aviso.id for aviso in avisos] == ['personas.W001']
    assert ALUMNO in avisos[0].msg
    assert not Group.objects.filter(name=ALUMNO).exists()


@pytest.mark.django_db
def test_tabla_ausente():
    with patch.object(connection.introspection, 'table_names', return_value=[]):
        assert comprobar_roles(databases=['default'])[0].id == 'personas.W002'


@pytest.mark.django_db
def test_conexion_fallida():
    with patch.object(connection.introspection, 'table_names', side_effect=OperationalError):
        assert comprobar_roles(databases=['default'])[0].id == 'personas.W003'


def test_router_excluye_alias():
    with patch('apps.personas.checks.router.allow_migrate_model', return_value=False):
        assert comprobar_roles(databases=['default']) == []
