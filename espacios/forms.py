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
        queryset=Espacio.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Dependencias"
    )

    class Meta:
        model = Espacio
        fields = ['dependencias']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)  # Obtener el request si se pasa
        super().__init__(*args, **kwargs)

        if request and request.user.is_superuser:
            self.fields['dependencias'].queryset = Espacio.objects.filter(
                codigo_postal=request.user.codigo_postal
            )