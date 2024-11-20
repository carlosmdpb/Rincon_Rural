from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from espacios.models import Espacio
from reservas.forms import ReservaForm
from reservas.models import Reserva
from .forms import RegistroForm
from django.contrib.auth.decorators import login_required

# Vista para el registro de usuarios
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('login')  # Redirige al inicio después del registro
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

# Vista genérica para el inicio de sesión
class LoginUsuario(LoginView):
    template_name = 'usuarios/login.html'

# Vista para el cierre de sesión
def cerrar_sesion(request):
    logout(request)
    return redirect('/')

@login_required
def perfil_usuario(request):
    espacios = Espacio.objects.filter(disponible=True)  # Espacios disponibles
    reservas = Reserva.objects.filter(usuario=request.user)  # Reservas del usuario actual
    return render(request, 'usuarios/perfil.html', {'usuario': request.user, 'espacios': espacios, 'reservas': reservas})

@login_required
def reservar_espacio(request, espacio_id):
    espacio = get_object_or_404(Espacio, id=espacio_id)

    if request.method == 'POST':
        form = ReservaForm(request.POST, espacio=espacio)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.espacio = espacio
            reserva.usuario = request.user
            reserva.save()
            messages.success(request, "¡Reserva creada con éxito!")
            return redirect('perfil_usuario')
    else:
        form = ReservaForm(espacio=espacio)

    return render(request, 'usuarios/reservar_espacio.html', {'form': form, 'espacio': espacio})
