"""Instalación de roles; nunca restaura permisos personalizados (sección 3)."""

from django.apps import apps as global_apps
from django.core.exceptions import ImproperlyConfigured
from django.db import router, transaction

from .roles import PERMISOS_INICIALES


def crear_roles(sender, *, apps=global_apps, using, **kwargs):
    # migrate aporta su registro histórico; flush usa el registro global (como auth).
    try:
        grupo_model = apps.get_model('auth', 'Group')
        permiso_model = apps.get_model('auth', 'Permission')
    except LookupError:
        return  # Un estado de migración parcial todavía puede no incluir auth.
    if not all(router.allow_migrate_model(using, model) for model in (grupo_model, permiso_model)):
        return

    with transaction.atomic(using=using):
        for nombre, codigos in PERMISOS_INICIALES.items():
            grupo, creado = grupo_model.objects.using(using).get_or_create(name=nombre)
            if not creado:
                continue
            permisos = list(permiso_model.objects.using(using).filter(
                content_type__app_label='personas',
                content_type__model='persona',
                codename__in=codigos,
            ))
            faltantes = set(codigos) - {permiso.codename for permiso in permisos}
            if faltantes:
                raise ImproperlyConfigured(
                    'No se pudieron inicializar los roles: faltan permisos de Persona: '
                    + ', '.join(sorted(faltantes))
                )
            grupo.permissions.add(*permisos)
