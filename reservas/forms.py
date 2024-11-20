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
        fields = ['fecha_inicio', 'fecha_fin']

    def __init__(self, *args, **kwargs):
        self.espacio = kwargs.pop('espacio', None)  # Recibimos el espacio desde la vista
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        # Validar que las fechas estén presentes
        if not fecha_inicio or not fecha_fin:
            return cleaned_data

        # Validar que la fecha de inicio sea menor que la fecha de fin
        if fecha_inicio >= fecha_fin:
            raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")

        # Validar que el horario esté dentro del rango permitido del espacio
        if self.espacio:
            if fecha_inicio.time() < self.espacio.hora_apertura or fecha_fin.time() > self.espacio.hora_cierre:
                raise ValidationError(
                    f"El horario debe estar entre {self.espacio.hora_apertura} y {self.espacio.hora_cierre}."
                )

            # Validar que no haya conflictos con reservas existentes
            reservas_existentes = Reserva.objects.filter(
                espacio=self.espacio,
                fecha_fin__gt=fecha_inicio,  # Terminan después de que comienza la nueva
                fecha_inicio__lt=fecha_fin  # Comienzan antes de que termine la nueva
            )
            if reservas_existentes.exists():
                raise ValidationError("Este espacio ya está reservado en el horario seleccionado.")

        return cleaned_data
