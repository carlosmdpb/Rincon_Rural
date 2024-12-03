from django.db import models

# Create your models here.
class Espacio(models.Model):
    nombre = models.CharField(max_length=100)
    capacidad = models.PositiveIntegerField()
    descripcion = models.TextField(blank=True, null=True)
    disponible = models.BooleanField(default=True)
    hora_apertura = models.TimeField()
    hora_cierre = models.TimeField()
    dependencias = models.ManyToManyField('self', symmetrical=False, blank=True)
    codigo_postal = models.CharField(max_length=5)
    autorizacion = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre
    
    def esta_disponible_en_horario(self, hora):
        """
        Verifica si el espacio está disponible a una hora específica.
        """
        return self.hora_apertura <= hora <= self.hora_cierre
    
    def esta_disponible(self):
        """
        Verifica si el espacio está disponible, considerando sus dependencias.
        """
        if not self.disponible:
            return False
        for dependencia in self.dependencias.all():
            if not dependencia.disponible:
                return False
        return True
    
class ImagenEspacio(models.Model):
    espacio = models.ForeignKey(Espacio, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='static/images/espacios/')

    def __str__(self):
        return f"Imagen de {self.espacio.nombre}"