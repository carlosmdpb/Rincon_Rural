from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.
class Usuario(AbstractUser):
    ROLES = [
        ('ciudadano', 'Ciudadano'),
        ('administrador', 'Administrador'),
    ]
    rol = models.CharField(max_length=15, choices=ROLES, default='ciudadano')
    dni = models.CharField(max_length=15, unique=True, blank=True, null=True)  
    codigo_postal = models.CharField(max_length=5, blank=False, null=False)
    contador = models.IntegerField(default=0)


    # Agrega related_name únicos para evitar conflictos
    groups = models.ManyToManyField(
        Group,
        related_name="usuarios_grupos",  # Cambia el nombre por uno único
        blank=True,
        help_text="Grupos a los que pertenece el usuario.",
        verbose_name="grupos",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="usuarios_permisos",  # Cambia el nombre por uno único
        blank=True,
        help_text="Permisos específicos del usuario.",
        verbose_name="permisos de usuario",
    )

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"