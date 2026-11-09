from django import forms

from .models import Usuario


class FormularioUsuario(forms.ModelForm):
    """C39: solo estado y condición de Administrador; el acceso se otorga en #23."""

    class Meta:
        model = Usuario
        fields = ('is_active', 'is_staff', 'is_superuser')

    def clean(self):
        datos = super().clean()
        for campo in self.Meta.fields:
            if campo in datos:
                setattr(self.instance, campo, datos[campo])
        self.instance.validar_administrador_activo()
        return datos
