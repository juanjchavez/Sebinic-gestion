"""Pruebas de Persona: identificación, natural/jurídica, correo opcional y ACC-03."""

import datetime

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.personas.models import Persona


def _persona(**campos):
    """Persona natural válida por defecto; los argumentos sobrescriben campos."""
    datos = {
        'tipo': 'natural',
        'nombres': 'Luis',
        'apellidos': 'Mora',
        'tipo_identificacion': 'cedula',
        'numero_identificacion': '001-120390-0002B',
    }
    datos.update(campos)
    return Persona(**datos)


@pytest.mark.django_db
@pytest.mark.parametrize('tipo,apellidos', [('natural', 'Mora'), ('juridica', '')])
@pytest.mark.parametrize('nombres', ['', '   ', '\t\n'])
def test_nombres_vacios_tras_normalizar_se_rechazan(tipo, apellidos, nombres):
    persona = _persona(tipo=tipo, apellidos=apellidos, nombres=nombres)

    with pytest.raises(ValidationError) as exc:
        persona.full_clean()

    assert 'nombres' in exc.value.message_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    'tipo,apellidos,nombres',
    [('natural', 'Mora', 'Luis'), ('juridica', '', 'Iglesia Bautista')],
)
def test_nombres_validos_con_espacios_se_normalizan(tipo, apellidos, nombres):
    persona = _persona(tipo=tipo, apellidos=apellidos, nombres=f'  {nombres}  ')

    persona.full_clean()
    persona.save()
    persona.refresh_from_db()

    assert persona.nombres == nombres


@pytest.mark.django_db
def test_identificacion_se_normaliza():
    persona = _persona(numero_identificacion=' 001-120390-0001a ')
    persona.full_clean()
    persona.save()
    persona.refresh_from_db()
    assert persona.numero_identificacion == '0011203900001A'


@pytest.mark.django_db
def test_identificacion_se_normaliza_con_save_directo():
    persona = Persona.objects.create(
        tipo='natural',
        nombres='Rosa',
        apellidos='Vega',
        tipo_identificacion='pasaporte',
        numero_identificacion=' c-123 456 ',
    )
    persona.refresh_from_db()
    assert persona.numero_identificacion == 'C123456'


@pytest.mark.django_db
def test_identificacion_duplicada_se_rechaza_indicando_a_quien_pertenece(persona_natural):
    persona = _persona(numero_identificacion='0011203900001a')
    with pytest.raises(ValidationError) as exc:
        persona.full_clean()
    assert 'numero_identificacion' in exc.value.message_dict
    assert 'Ana López' in exc.value.message_dict['numero_identificacion'][0]


@pytest.mark.django_db
def test_mismo_numero_con_otro_tipo_se_acepta(persona_natural):
    persona = _persona(tipo_identificacion='pasaporte', numero_identificacion='001-120390-0001A')
    persona.full_clean()


@pytest.mark.django_db
def test_constraint_bd_impide_identificacion_duplicada(persona_natural):
    with pytest.raises(IntegrityError), transaction.atomic():
        Persona.objects.create(
            tipo='natural',
            nombres='Otra',
            apellidos='Persona',
            tipo_identificacion='cedula',
            numero_identificacion='001-120390-0001A',
        )


@pytest.mark.django_db
def test_natural_sin_apellidos_se_rechaza():
    persona = _persona(apellidos='')
    with pytest.raises(ValidationError) as exc:
        persona.full_clean()
    assert 'apellidos' in exc.value.message_dict


@pytest.mark.django_db
@pytest.mark.regla('ACC-03')
def test_juridica_con_razon_social_y_sin_apellidos_se_acepta():
    institucion = Persona(
        tipo='juridica',
        nombres='Iglesia Bautista Norte',
        tipo_identificacion='ruc',
        numero_identificacion='J0310000000002',
    )
    institucion.full_clean()


@pytest.mark.django_db
def test_juridica_con_apellidos_o_fecha_nacimiento_se_rechaza():
    institucion = Persona(
        tipo='juridica',
        nombres='Iglesia Bautista Sur',
        apellidos='Pérez',
        tipo_identificacion='ruc',
        numero_identificacion='J0310000000003',
        fecha_nacimiento=datetime.date(1990, 1, 1),
    )
    with pytest.raises(ValidationError) as exc:
        institucion.full_clean()
    assert 'apellidos' in exc.value.message_dict
    assert 'fecha_nacimiento' in exc.value.message_dict


@pytest.mark.django_db
@pytest.mark.regla('ACC-06')
def test_persona_sin_correo_se_guarda():
    persona = _persona(correo='')
    persona.full_clean()
    persona.save()
    assert Persona.objects.filter(pk=persona.pk, correo='').exists()


@pytest.mark.django_db
def test_correo_mal_formado_se_rechaza():
    persona = _persona(correo='ana@')
    with pytest.raises(ValidationError) as exc:
        persona.full_clean()
    assert 'correo' in exc.value.message_dict


@pytest.mark.django_db
@pytest.mark.regla('ACC-03')
def test_no_se_puede_cambiar_a_juridica_con_usuario(usuario):
    persona = usuario.persona
    persona.tipo = 'juridica'
    persona.apellidos = ''
    with pytest.raises(ValidationError) as exc:
        persona.full_clean()
    assert 'tipo' in exc.value.message_dict
