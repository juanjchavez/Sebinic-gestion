from django.apps import AppConfig


class PersonasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.personas'
    label = 'personas'
    verbose_name = 'Personas'

    def ready(self):
        from django.db.models.signals import post_migrate

        from . import checks  # noqa: F401: registra comprobaciones, sin consultar BD.
        from .signals import crear_roles

        post_migrate.connect(
            crear_roles, sender=self, dispatch_uid='personas.crear_roles',
        )
