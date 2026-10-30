"""Reglas de normalización de identificaciones y correos de la app personas.

Un único lugar para estas reglas, usado por el modelo, el manager y el selector,
para que la misma cédula o el mismo correo se comparen siempre igual.
"""

import re


def normalizar_identificacion(valor: str | None) -> str:
    """Quita espacios y guiones, y pasa a mayúsculas.

    Ejemplo: ' 001-120390-0001a ' -> '0011203900001A'.
    """
    return re.sub(r"[\s\-]+", "", valor or "").upper()


def normalizar_correo(valor: str | None) -> str:
    """Quita espacios alrededor y pasa a minúsculas (ACC-05: el correo no distingue mayúsculas)."""
    return (valor or "").strip().lower()
