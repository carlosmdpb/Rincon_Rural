# espacios/forms.py
from django import forms
from .models import Espacio
from django.urls import reverse
from django.utils.safestring import mark_safe

class EspacioForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombre', 'capacidad', 'descripcion', 'disponible', 'hora_apertura', 'hora_cierre']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar el botón al lado del campo "capacidad"
        if self.instance.pk:
            gestionar_dependencias_url = reverse('admin:espacios_espacio_dependencias', args=[self.instance.pk])
            self.fields['capacidad'].help_text = mark_safe(
                f'<a href="{gestionar_dependencias_url}" class="button" style="margin-left: 10px;">Gestionar Dependencias</a>'
            )
            
class GestionarDependenciasForm(forms.ModelForm):
    dependencias = forms.ModelMultipleChoiceField(
        queryset=Espacio.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Usar una lista de checkboxes
        required=False,
        label="Dependencias"
    )

    class Meta:
        model = Espacio
        fields = ['dependencias']
