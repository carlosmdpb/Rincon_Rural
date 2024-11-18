from django.shortcuts import render, redirect
from .models import Reserva
from .forms import ReservaForm

# Create your views here.
def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user  # Asigna el usuario actual a la reserva
            reserva.save()
            return redirect('listar_reservas')
    else:
        form = ReservaForm()
    return render(request, 'crear.html', {'form': form})

def listar_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user)
    return render(request, 'listar.html', {'reservas': reservas})