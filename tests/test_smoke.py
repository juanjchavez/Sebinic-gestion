import pytest
from django.conf import settings
from django.contrib.auth import get_user_model


def test_settings_cargan():
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"


@pytest.mark.django_db
def test_consulta_simple_a_la_bd():
    assert get_user_model().objects.count() == 0


@pytest.mark.django_db
@pytest.mark.regla("EJEMPLO-01")
def test_ejemplo_de_prueba_con_marcador_de_regla():
    # Solo demuestra el marcador `regla`; la prueba de humo ya cubre la consulta a la BD.
    # Las pruebas de reglas de negocio reales (COB-*, REG-*, BIB-*) se agregan en
    # cada ticket funcional, junto al modelo o servicio que las implementa.
    assert True
