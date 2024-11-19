from datetime import time
from django.shortcuts import redirect, render, get_object_or_404
from .models import Espacio
from .forms import EspacioForm

# Create your views here.

def listar_espacios(request):
    filtro_reserva = request.GET.get('reserva_activa', 'todo')
    espacios = Espacio.objects.all()
    if filtro_reserva == 'si':
        espacios = espacios.filter(reserva__isnull=False)
    elif filtro_reserva == 'no':
        espacios = espacios.filter(reserva__isnull=True)
    return render(request, 'espacios/listar.html', {'espacios': espacios, 'filtro_reserva': filtro_reserva})

def detalle_espacio(request, espacio_id):
    espacio = get_object_or_404(Espacio, id=espacio_id)
    return render(request, 'espacios/detalle.html', {'espacio': espacio})

def verificar_disponibilidad(request, espacio_id):
    espacio = Espacio.objects.get(id=espacio_id)
    hora_actual = time(15, 30)  # Hora actual: 3:30 PM

    if espacio.esta_disponible_en_horario(hora_actual):
        mensaje = f"{espacio.nombre} está disponible ahora."
    else:
        mensaje = f"{espacio.nombre} no está disponible en este horario."

    return render(request, 'disponibilidad.html', {'mensaje': mensaje})

def crear_espacio(request):
    if request.method == 'POST':
        form = EspacioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_espacios')
    else:
        form = EspacioForm()
    return render(request, 'espacios/crear.html', {'form': form})

def welcome(request):
    return render(request, 'welcome.html')