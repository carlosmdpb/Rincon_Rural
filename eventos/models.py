from django.db import models
from espacios.models import Espacio

# Create your models here.
class Evento(models.Model):
    nombre = models.CharField(max_length=100)
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    descripcion = models.TextField(blank=True, null=True)
    codigo_postal = models.CharField(max_length=5, default="00000")

    def __str__(self):
        return self.nombre