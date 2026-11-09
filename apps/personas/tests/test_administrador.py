from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest
from django.core.exceptions import ValidationError
from django.db import close_old_connections, connection, connections, transaction

from apps.personas.models import Usuario

pytestmark = [pytest.mark.django_db, pytest.mark.regla('Sección 3', 'C39', 'TEC-07')]


@pytest.fixture
def administrador():
    return Usuario.objects.create_superuser(email='admin@seminario.org')


@pytest.mark.parametrize('indicador', ['is_active', 'is_staff', 'is_superuser'])
def test_no_retirar_ultimo_administrador(administrador, indicador):
    antes = administrador.historial.count()
    setattr(administrador, indicador, False)
    with pytest.raises(ValidationError, match='Administrador activo'):
        administrador.save()
    administrador.refresh_from_db()
    assert getattr(administrador, indicador) is True
    assert administrador.historial.count() == antes


def test_se_permite_si_queda_otro(administrador):
    Usuario.objects.create_superuser(email='otro@seminario.org')
    administrador.is_active = False
    administrador.save(update_fields=['is_active'])
    administrador.refresh_from_db()
    assert not administrador.is_active


@pytest.mark.parametrize('indicador', ['is_active', 'is_staff', 'is_superuser'])
def test_otro_no_operativo_no_cuenta(administrador, indicador):
    Usuario.objects.create_user(email='otro@seminario.org', **{
        'is_active': indicador != 'is_active',
        'is_staff': indicador != 'is_staff',
        'is_superuser': indicador != 'is_superuser',
    })
    administrador.is_active = False
    with pytest.raises(ValidationError):
        administrador.save(update_fields=['is_active'])


def test_update_fields_solo_valida_lo_que_se_persiste(administrador):
    administrador.is_active = False
    administrador.email = 'nuevo@seminario.org'
    administrador.save(update_fields=['email'])
    administrador.refresh_from_db()
    assert administrador.is_active
    assert administrador.email == 'nuevo@seminario.org'


def test_update_fields_no_confunde_estado_en_memoria(administrador):
    administrador.is_staff = False
    administrador.save(update_fields=['is_active'])
    administrador.refresh_from_db()
    assert administrador.is_staff


@pytest.mark.django_db(transaction=True)
def test_dos_bajas_concurrentes_conservan_un_administrador():
    assert connection.vendor == 'postgresql'
    usuarios = [Usuario.objects.create_superuser(email=f'admin{i}@seminario.org') for i in range(2)]
    intentos = [Event(), Event()]

    def desactivar(indice):
        close_old_connections()
        try:
            usuario = Usuario.objects.get(pk=usuarios[indice].pk)
            usuario.is_active = False

            def observar(execute, sql, params, many, context):
                if 'FOR UPDATE' in sql:
                    intentos[indice].set()
                return execute(sql, params, many, context)

            with connections['default'].execute_wrapper(observar):
                with transaction.atomic():
                    with connections['default'].cursor() as cursor:
                        cursor.execute("SET LOCAL lock_timeout = '5s'")
                    usuario.save(update_fields=['is_active'])
            return 'guardado'
        except ValidationError:
            return 'rechazado'
        finally:
            connections['default'].close()

    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        with transaction.atomic():
            list(Usuario.objects.filter(is_superuser=True).order_by('pk').select_for_update())
            futuros = [ejecutor.submit(desactivar, i) for i in range(2)]
            assert all(evento.wait(5) for evento in intentos)
        resultados = [futuro.result(timeout=10) for futuro in futuros]
    assert sorted(resultados) == ['guardado', 'rechazado']
    assert Usuario.objects.filter(is_active=True, is_staff=True, is_superuser=True).count() == 1
