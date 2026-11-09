from django.contrib.admin.apps import AdminConfig


class ConfiguracionAdmin(AdminConfig):
    default_site = 'config.admin.SitioAdministrador'
