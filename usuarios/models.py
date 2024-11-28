from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import smtplib
from email.mime.text import MIMEText

# Create your models here.
class Usuario(AbstractUser):
    ROLES = [
        ('ciudadano', 'Ciudadano'),
        ('administrador', 'Administrador'),
    ]
    nombre = models.CharField(max_length=50, blank=False, null=False, default='')
    apellidos = models.CharField(max_length=50, blank=False, null=False, default='')
    rol = models.CharField(max_length=15, choices=ROLES, default='ciudadano')
    dni = models.CharField(max_length=15, unique=True, blank=True, null=True)  
    codigo_postal = models.CharField(max_length=5, blank=False, null=False)
    contador = models.IntegerField(default=0)
    REQUIRED_FIELDS = ['codigo_postal']


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
    
    def save(self, *args, **kwargs):
        if self.pk:  # Verificar si el usuario ya existe
            usuario_original = Usuario.objects.get(pk=self.pk)
            # Si el usuario pasa de inactivo a activo
            if not usuario_original.is_active and self.is_active:
                self.enviar_correo_activacion()
        super().save(*args, **kwargs)

    def enviar_correo_activacion(self):
        """
        Enviar correo al usuario cuando su cuenta es activada.
        """
        subject = "Tu cuenta ha sido activada"
        sender = 'rinconrural24@gmail.com'
        password = 'njpb zzdb dujv daef'
        body = (
            f"Hola {self.username},\n\n"
            "Tu cuenta ha sido activada y ahora puedes iniciar sesión en nuestra plataforma.\n\n"
            "Gracias por formar parte de nuestra comunidad.\n\n"
            "Atentamente,\nEl equipo de Rincón Rural."
        )

        self._enviar_correo(subject, body, sender, [self.email], password)

    def _enviar_correo(self, subject, body, sender, recipients, password):
        """
        Lógica interna para enviar un correo.
        """
        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = ", ".join(recipients)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, message.as_string())