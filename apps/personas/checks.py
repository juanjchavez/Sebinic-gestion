"""Comprobación de nombres canónicos de roles (sección 3, C39)."""

from django.contrib.auth.models import Group
from django.core.checks import Tags, Warning, register
from django.db import InterfaceError, OperationalError, connections, router

from .roles import ROLES


@register(Tags.database)
def comprobar_roles(app_configs=None, databases=None, **kwargs):
    avisos = []
    for alias in databases or ():
        if not router.allow_migrate_model(alias, Group):
            continue
        try:
            conexion = connections[alias]
            if Group._meta.db_table not in conexion.introspection.table_names():
                avisos.append(Warning(
                    f'[{alias}] La tabla de grupos todavía no existe.',
                    hint='Ejecute migrate antes de comprobar los roles.',
                    id='personas.W002',
                ))
                continue
            existentes = set(
                Group.objects.using(alias).filter(name__in=ROLES).values_list('name', flat=True)
            )
            faltantes = set(ROLES) - existentes
            if faltantes:
                avisos.append(Warning(
                    f'[{alias}] Faltan grupos del sistema: {", ".join(sorted(faltantes))}.',
                    hint=(
                        'Investigue si fueron renombrados antes de ejecutar migrate; '
                        'no se transfieren miembros.'
                    ),
                    id='personas.W001',
                ))
        except (OperationalError, InterfaceError):
            avisos.append(Warning(
                f'[{alias}] No se pudo conectar para comprobar los roles.',
                hint='Revise la conexión y vuelva a ejecutar check --database.',
                id='personas.W003',
            ))
    return avisos
