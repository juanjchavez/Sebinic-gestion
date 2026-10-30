"""Lecturas de personas que usan las demás apps (data model §D3: las lecturas van por selectores)."""

from .models import Persona
from .normalizacion import normalizar_identificacion


def persona_por_identificacion(tipo_identificacion: str, numero_identificacion: str) -> Persona | None:
    """Devuelve la persona con ese tipo y número de identificación, o None si no existe.

    El número se normaliza igual que al guardarlo, así que ' 001-120390-0001a ' encuentra
    la cédula registrada como '0011203900001A'.
    """
    return Persona.objects.filter(
        tipo_identificacion=tipo_identificacion,
        numero_identificacion=normalizar_identificacion(numero_identificacion),
    ).first()
