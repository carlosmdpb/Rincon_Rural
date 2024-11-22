from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario 

class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Usuario inactivo hasta que se apruebe
        print(user.is_active)
        if commit:
            user.save()
            # Crear la solicitud de registro automáticamente
            from solicitud.models import SolicitudRegistro
            SolicitudRegistro.objects.create(usuario=user)
        return user
