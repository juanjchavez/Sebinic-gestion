"""Pruebas del selector de personas por identificación."""

import pytest

from apps.personas.selectores import persona_por_identificacion


@pytest.mark.django_db
def test_persona_por_identificacion_normaliza_el_numero_buscado(persona_natural):
    assert persona_por_identificacion('cedula', ' 001 120390 0001a') == persona_natural


@pytest.mark.django_db
def test_persona_por_identificacion_respeta_el_tipo(persona_natural):
    assert persona_por_identificacion('pasaporte', '0011203900001A') is None


@pytest.mark.django_db
def test_persona_por_identificacion_devuelve_none_si_no_existe(persona_natural):
    assert persona_por_identificacion('cedula', '999-999999-9999Z') is None
