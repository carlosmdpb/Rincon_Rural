from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
import re

class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'dni', 'codigo_postal', 'password1', 'password2']

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if not re.match(r'^\d{8}[A-Z]$', dni):
            raise forms.ValidationError("El DNI debe tener 8 números seguidos de una letra mayúscula.")
        return dni

    def clean_codigo_postal(self):
        codigo_postal = self.cleaned_data.get('codigo_postal')
        if not re.match(r'^\d{5}$', codigo_postal):
            raise forms.ValidationError("El código postal debe tener exactamente 5 dígitos.")
        return codigo_postal

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Usuario inactivo hasta que se apruebe
        if commit:
            user.save()
            # Crear la solicitud de registro automáticamente
            from solicitud.models import SolicitudRegistro
            SolicitudRegistro.objects.create(usuario=user)
        return user
