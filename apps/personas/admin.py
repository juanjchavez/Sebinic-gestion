from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect

from .forms import FormularioUsuario
from .models import Persona, Usuario


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'tipo', 'numero_identificacion', 'correo')
    search_fields = ('nombres', 'apellidos', 'numero_identificacion', 'correo')
    list_filter = ('tipo',)
    list_select_related = ('usuario',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')

    def get_readonly_fields(self, request, obj=None):
        # C42/ACC-05: el cambio coordinado de correo pertenece al servicio #23.
        return ('correo',) if obj and hasattr(obj, 'usuario') else ()


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    form = FormularioUsuario
    list_display = ('email', 'persona', 'is_active', 'is_superuser')
    list_filter = ('is_active', 'is_superuser')
    search_fields = ('email', 'persona__nombres', 'persona__apellidos')
    list_select_related = ('persona',)
    readonly_fields = ('email', 'persona', 'groups', 'user_permissions', 'date_joined', 'last_login')
    fields = readonly_fields + ('is_active', 'is_staff', 'is_superuser')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        try:
            return super().changeform_view(request, object_id, form_url, extra_context)
        except ValidationError as error:
            # C39: una carrera puede rechazar save después de validar el formulario.
            # Capturar fuera del atomic del panel revierte también su registro de cambios.
            self.message_user(request, ' '.join(error.messages), level=messages.ERROR)
            return HttpResponseRedirect(request.path)
