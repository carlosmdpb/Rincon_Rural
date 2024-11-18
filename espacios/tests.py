from django.test import TestCase

# Create your tests here.
from datetime import time
from django.test import TestCase
from espacios.models import Espacio

class EspacioTests(TestCase):
    def setUp(self):
        self.espacio = Espacio.objects.create(
            nombre="Sala de reuniones",
            hora_apertura=time(8, 0),
            hora_cierre=time(20, 0),
        )

    def test_espacio_disponible(self):
        hora = time(10, 0)
        self.assertTrue(self.espacio.esta_disponible_en_horario(hora))

    def test_espacio_no_disponible(self):
        hora = time(22, 0)
        self.assertFalse(self.espacio.esta_disponible_en_horario(hora))