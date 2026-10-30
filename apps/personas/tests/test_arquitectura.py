"""Pruebas de arquitectura: apps/personas no depende de ninguna otra app (TEC-11)."""

import ast
from pathlib import Path

import pytest

# Apps del proyecto que personas no puede importar (TEC-11: personas no depende de ninguna).
APPS_PROHIBIDAS = (
    'apps.admision_cobranza',
    'apps.registro_academico',
    'apps.biblioteca',
    'apps.configuracion',
    'admision_cobranza',
    'registro_academico',
    'biblioteca',
    'configuracion',
)


def _es_prohibido(modulo: str) -> bool:
    return any(modulo == app or modulo.startswith(app + '.') for app in APPS_PROHIBIDAS)


def _modulos_importados(archivo: Path):
    arbol = ast.parse(archivo.read_text(encoding='utf-8'), filename=str(archivo))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                yield alias.name
        elif isinstance(nodo, ast.ImportFrom) and nodo.level == 0 and nodo.module:
            # Los imports relativos (level > 0) quedan dentro de apps/personas.
            yield nodo.module


@pytest.mark.regla('TEC-11')
def test_personas_no_importa_otras_apps():
    raiz = Path(__file__).resolve().parents[1]  # apps/personas
    infractores = []
    for archivo in sorted(raiz.rglob('*.py')):
        for modulo in _modulos_importados(archivo):
            if _es_prohibido(modulo):
                infractores.append(f'{archivo.relative_to(raiz)} importa {modulo}')

    assert not infractores, (
        'apps/personas no puede depender de otras apps (TEC-11): ' + '; '.join(infractores)
    )
