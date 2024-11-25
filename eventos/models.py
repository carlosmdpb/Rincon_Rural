from django.db import models
from espacios.models import Espacio
from reservas.models import Reserva
from django.utils.timezone import localtime
from django.core.mail import send_mail
from django.conf import settings
import smtplib
from email.mime.text import MIMEText

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
    
    def save(self, *args, **kwargs):
        # Buscar reservas que coincidan con el espacio y el día del evento
        inicio_dia = localtime(self.fecha_inicio).replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = localtime(self.fecha_inicio).replace(hour=23, minute=59, second=59, microsecond=999999)

        reservas_a_eliminar = Reserva.objects.filter(
            espacio=self.espacio,
            fecha_inicio__lt=self.fecha_fin,  # Reservas que comienzan antes de que termine el evento
            fecha_fin__gt=self.fecha_inicio   # Reservas que terminan después de que comienza el evento
        )
        subject = "Reservas eliminadas"
        body = "Se han eliminado las siguientes reservas: " + str(reservas_a_eliminar)
        sender = 'rinconrural24@gmail.com'
        password = 'njpb zzdb dujv daef'
        usuario_email_send = []
        for reserva in reservas_a_eliminar:
            usuario = reserva.usuario.email
            if usuario not in usuario_email_send:
                usuario_email_send.append(usuario)
                self.send_mail(subject, body, sender, usuario, password)

        # Eliminar las reservas
        reservas_a_eliminar.delete()

        # Llamar al método save del modelo base para guardar el evento
        super().save(*args, **kwargs)
    
            
    def send_mail(self, subject, body, sender, recipients, password):
        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = ", ".join(recipients)
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, message.as_string())