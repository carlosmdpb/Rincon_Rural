from django.db import models

class Calificacion(models.Model):
    puntuacion_total = models.PositiveIntegerField(default=0)  # Suma de todas las puntuaciones
    numero_votos = models.PositiveIntegerField(default=0)  # Número de personas que han votado

    @property
    def promedio(self):
        if self.numero_votos > 0:
            return self.puntuacion_total / self.numero_votos
        return 0  # Si nadie ha votado, el promedio es 0

    def __str__(self):
        return f"{self.espacio.nombre}: {self.promedio:.2f} ({self.numero_votos} votos)"
