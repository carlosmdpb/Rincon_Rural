from django.db import models
from django.conf import settings
from espacios.models import Espacio
import uuid
import smtplib
from email.mime.text import MIMEText

class Reserva(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    codigo_postal = models.CharField(max_length=5)
    grupo_reserva = models.UUIDField(default=uuid.uuid4, editable=False)  # Campo para agrupar
    autorizada = models.BooleanField(default=False)
    ESTADOS = [
        ('activa', 'Activa'),
        ('cancelada', 'Cancelada'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activa')

    def __str__(self):
        return f"Reserva de {self.usuario} para {self.espacio.nombre} ({self.estado})"
    
    def save(self, *args, **kwargs):
        """
        Antes de guardar la reserva, verifica si cambia a autorizada y envía un correo.
        """
        if self.pk:  # Si ya existe la reserva
            reserva_original = Reserva.objects.get(pk=self.pk)
            # Si cambia de no autorizada a autorizada
            if not reserva_original.autorizada and self.autorizada:
                self.enviar_correo_autorizacion()
        
        # Asigna el código postal si no está definido
        if self.usuario:
            self.codigo_postal = self.usuario.codigo_postal

        super().save(*args, **kwargs)

    def enviar_correo_autorizacion(self):
        """
        Envía un correo al usuario cuando la reserva es autorizada.
        """
        subject = "Tu reserva ha sido autorizada"
        sender = 'rinconrural24@gmail.com'
        password = 'njpb zzdb dujv daef'  # Cambiar por credenciales seguras en producción
        body = (
            f"Hola {self.usuario.nombre},\n\n"
            f"Nos complace informarte que tu reserva para el espacio '{self.espacio.nombre}' ha sido autorizada.\n\n"
            f"Detalles de la reserva:\n"
            f"Fecha: {self.fecha_inicio.strftime('%d/%m/%Y')}\n"
            f"Hora: {self.fecha_inicio.strftime('%H:%M')} - {self.fecha_fin.strftime('%H:%M')}\n\n"
            "Gracias por confiar en nuestro servicio.\n\n"
            "Atentamente,\nEl equipo de Rincón Rural."
        )

        self._enviar_correo(subject, body, sender, [self.usuario.email], password)

    def _enviar_correo(self, subject, body, sender, recipients, password):
        """
        Lógica para enviar el correo.
        """
        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = ", ".join(recipients)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
                smtp_server.login(sender, password)
                smtp_server.sendmail(sender, recipients, message.as_string())
        except Exception as e:
            print(f"Error al enviar correo: {e}")