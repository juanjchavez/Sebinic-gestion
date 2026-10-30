"""Fixtures compartidas de las pruebas de la app personas.

Las fixtures tocan la base de datos: las pruebas que las usan llevan @pytest.mark.django_db.
"""

import pytest

from apps.personas.models import Persona, Usuario

CLAVE_PRUEBA = 'clave-de-prueba-123'


@pytest.fixture
def persona_natural(db):
    return Persona.objects.create(
        tipo='natural',
        nombres='Ana',
        apellidos='López',
        tipo_identificacion='cedula',
        numero_identificacion='001-120390-0001A',
        correo='ana@x.org',
    )


@pytest.fixture
def persona_juridica(db):
    return Persona.objects.create(
        tipo='juridica',
        nombres='Iglesia Bautista Central',
        tipo_identificacion='ruc',
        numero_identificacion='J0310000000001',
    )


@pytest.fixture
def usuario(persona_natural):
    return Usuario.objects.create_user(
        email='Ana@x.org',
        password=CLAVE_PRUEBA,
        persona=persona_natural,
    )
