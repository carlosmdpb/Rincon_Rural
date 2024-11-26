from django.db import models
from django.conf import settings
from espacios.models import Espacio
import uuid

class Reserva(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    codigo_postal = models.CharField(max_length=5)
    grupo_reserva = models.UUIDField(default=uuid.uuid4, editable=False)  # Campo para agrupar
    ESTADOS = [
        ('activa', 'Activa'),
        ('cancelada', 'Cancelada'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activa')

    def __str__(self):
        return f"Reserva de {self.usuario} para {self.espacio.nombre} ({self.estado})"
    
    def save(self, *args, **kwargs):
        """
        Antes de guardar la reserva, asigna el código postal del usuario
        """
        if self.usuario:
            self.codigo_postal = self.usuario.codigo_postal
        super().save(*args, **kwargs)
