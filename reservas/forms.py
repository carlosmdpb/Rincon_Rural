# reservas/forms.py
from django import forms
from .models import Reserva

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['espacio', 'fecha_inicio', 'fecha_fin']
