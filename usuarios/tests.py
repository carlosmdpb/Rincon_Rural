from django.test import TestCase

# Create your tests here.
from reservas.models import Reserva
from espacios.models import Espacio
from django.utils.timezone import now, timedelta

espacio = Espacio.objects.get(nombre="Biblioteca")
usuario = Usuario.objects.first()  # O el usuario actual

fecha_inicio = make_aware(now())
fecha_fin = make_aware(now() + timedelta(hours=2))

try:
    reserva = Reserva(espacio=espacio, usuario=usuario, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    reserva.save()
    print("Reserva creada exitosamente.")
except ValidationError as e:
    print(f"Error al crear la reserva: {e}")
