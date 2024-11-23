from django import forms
from django.contrib.auth.forms import UserCreationForm

from reservas.models import Reserva
from .models import Usuario
from eventos.models import Evento
from espacios.models import Espacio
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


class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nombre', 'descripcion', 'fecha_inicio', 'fecha_fin']

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
            raise forms.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")

        return cleaned_data


class EspacioForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombre', 'descripcion', 'hora_apertura', 'hora_cierre', 'disponible']

    def clean(self):
        cleaned_data = super().clean()
        hora_apertura = cleaned_data.get("hora_apertura")
        hora_cierre = cleaned_data.get("hora_cierre")

        if hora_apertura and hora_cierre and hora_apertura >= hora_cierre:
            raise forms.ValidationError("La hora de apertura debe ser anterior a la hora de cierre.")

        return cleaned_data


class GestionReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['usuario', 'espacio', 'fecha_inicio', 'fecha_fin', 'estado']

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
            raise forms.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")

        return cleaned_data
