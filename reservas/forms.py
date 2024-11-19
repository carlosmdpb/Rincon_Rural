from django import forms
from django.core.exceptions import ValidationError
from .models import Reserva

class ReservaForm(forms.ModelForm):
    fecha_inicio = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label="Fecha de Inicio"
    )
    fecha_fin = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label="Fecha de Fin"
    )

    class Meta:
        model = Reserva
        fields = ['espacio', 'fecha_inicio', 'fecha_fin']

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        espacio = cleaned_data.get('espacio')

        # Validar que las fechas estén presentes
        if not fecha_inicio or not fecha_fin or not espacio:
            return cleaned_data

        # Validar que la fecha de inicio sea menor que la fecha de fin
        if fecha_inicio >= fecha_fin:
            raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")

        # Validar que el horario esté dentro del rango permitido del espacio
        if fecha_inicio.time() < espacio.hora_apertura or fecha_fin.time() > espacio.hora_cierre:
            raise ValidationError(
                f"El horario debe estar entre {espacio.hora_apertura} y {espacio.hora_cierre}."
            )

        return cleaned_data
