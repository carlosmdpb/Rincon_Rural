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

        # Filtrar reservas afectadas
        reservas_afectadas = Reserva.objects.filter(
            espacio=self.espacio,
            fecha_inicio__lt=self.fecha_fin,  # Reservas que comienzan antes de que termine el evento
            fecha_fin__gt=self.fecha_inicio   # Reservas que terminan después de que comienza el evento
        )

        # Identificar los grupos de reservas afectados
        grupos_afectados = reservas_afectadas.values_list('grupo_reserva', flat=True).distinct()

        # Obtener todas las reservas de los grupos afectados
        reservas_a_eliminar = Reserva.objects.filter(grupo_reserva__in=grupos_afectados)

        # Notificar a los usuarios afectados
        subject = "Reservas eliminadas"
        sender = 'rinconrural24@gmail.com'
        password = 'njpb zzdb dujv daef'
        usuarios_notificados = set()

        for reserva in reservas_a_eliminar:
            usuario_email = reserva.usuario.email
            if usuario_email not in usuarios_notificados:
                body = f"Estimado/a {reserva.usuario.username},\n\n"
                body += f"Se ha cancelado su reserva en el espacio '{reserva.espacio.nombre}' "
                body += f"debido a la programación de un evento que se superpone con su horario.\n\n"
                body += "Gracias por su comprensión."
                self.send_mail(subject, body, sender, [usuario_email], password)
                usuarios_notificados.add(usuario_email)

        # Eliminar todas las reservas afectadas
        reservas_a_eliminar.delete()

        # Guardar el evento
        super().save(*args, **kwargs)

    def send_mail(self, subject, body, sender, recipients, password):
        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = ", ".join(recipients)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, message.as_string())
