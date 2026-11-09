"""El panel es exclusivo del Administrador (sección 3, C25/C39)."""

from django.contrib.admin import AdminSite
from django.contrib.admin.forms import AdminAuthenticationForm


class AutenticacionAdministrador(AdminAuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_superuser:
            raise self.get_invalid_login_error()


class SitioAdministrador(AdminSite):
    login_form = AutenticacionAdministrador

    def has_permission(self, request):
        return super().has_permission(request) and request.user.is_superuser
