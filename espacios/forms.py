# espacios/forms.py
from django import forms
from .models import Espacio

class EspacioForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombre', 'capacidad', 'descripcion', 'hora_apertura', 'hora_cierre']
