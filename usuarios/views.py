from datetime import datetime, timedelta, timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from espacios.models import Espacio
from reservas.forms import ReservaForm
from reservas.models import Reserva
from .forms import RegistroForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Vista para el registro de usuarios
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_active = False  # Usuario inactivo hasta que sea aprobado
            usuario.save()
            messages.success(
                request,
                "El administrador tiene que aprobar tu solicitud de registro. "
                "Manténgase a la espera. Gracias por su paciencia."
            )
            return redirect('login')
        else:
            # Si el formulario no es válido, muestra los errores
            messages.error(request, "Por favor, corrige los errores en el formulario.")
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
    return render(request, 'usuarios/perfil.html', {
        'usuario': request.user,
        'espacios': espacios,
        'reservas': reservas
    })

@login_required
def reservar_espacio(request, espacio_id):
    espacio = get_object_or_404(Espacio, id=espacio_id)

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')

        if fecha and hora_inicio and hora_fin:
            try:
                fecha_inicio = datetime.strptime(f"{fecha} {hora_inicio}", "%Y-%m-%d %H:%M")
                fecha_fin = datetime.strptime(f"{fecha} {hora_fin}", "%Y-%m-%d %H:%M")

                # Validar que fecha_inicio < fecha_fin
                if fecha_inicio >= fecha_fin:
                    messages.error(request, "La hora de inicio debe ser anterior a la hora de fin.")
                    return render(request, 'usuarios/reservar_espacio.html', {'espacio': espacio})

                # Crear la reserva
                reserva = Reserva(
                    usuario=request.user,
                    espacio=espacio,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                )
                reserva.save()
                messages.success(request, "Reserva creada exitosamente.")
                return redirect('perfil_usuario')
            except Exception as e:
                messages.error(request, f"Error al procesar la reserva: {str(e)}")
        else:
            messages.error(request, "Por favor, selecciona una fecha y una franja horaria.")

    return render(request, 'usuarios/reservar_espacio.html', {'espacio': espacio})
