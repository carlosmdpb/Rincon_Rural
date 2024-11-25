from datetime import datetime, timedelta, timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from espacios.models import Espacio
from eventos.models import Evento
from reservas.forms import ReservaForm
from reservas.models import Reserva
from .forms import RegistroForm, EventoForm, EspacioForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils.timezone import make_aware, get_current_timezone, now

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
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = RegistroForm()

    storage = get_messages(request)
    for _ in storage:
        pass  # Limpia los mensajes de la sesión actual

    return render(request, 'usuarios/registro.html', {'form': form})

# Vista genérica para el inicio de sesión
class LoginUsuario(LoginView):
    template_name = 'usuarios/login.html'

    def get_success_url(self):
        # Redirige según el rol del usuario
        user = self.request.user
        if user.is_superuser:  # Caso de superusuario
            return reverse_lazy('admin:index')  # Redirige al panel de superusuario
        else:
            return reverse_lazy('perfil_usuario')

    def form_invalid(self, form):
        form.errors.clear()
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                messages.error(
                    self.request,
                    "El administrador tiene que aprobar tu solicitud de registro. "
                    "Manténgase a la espera. Gracias por su paciencia."
                )
            elif not check_password(password, user.password):
                messages.error(
                    self.request,
                    "Por favor, introduce una contraseña correcta."
                )
            else:
                messages.error(
                    self.request,
                    "Ocurrió un error inesperado. Por favor, inténtalo nuevamente."
                )
        except User.DoesNotExist:
            messages.error(
                self.request,
                "El nombre de usuario o la contraseña son incorrectos."
            )

        return self.render_to_response(self.get_context_data(form=form))

# Vista para el cierre de sesión
def cerrar_sesion(request):
    logout(request)
    return redirect('/')

@login_required
def perfil_usuario(request):
    # Obtener la hora actual y restarle una hora
    hora_actual = now() + timedelta(hours=2)

    # Espacios disponibles
    espacios = Espacio.objects.filter(disponible=True)
    
    # Reservas activas
    reservas_activas = Reserva.objects.filter(usuario=request.user, fecha_fin__gte=hora_actual)
    
    # Reservas pasadas
    reservas_pasadas = Reserva.objects.filter(usuario=request.user, fecha_fin__lt=hora_actual)
    
    return render(request, 'usuarios/perfil.html', {
        'usuario': request.user,
        'espacios': espacios,
        'reservas_activas': reservas_activas,
        'reservas_pasadas': reservas_pasadas
    })

@login_required
def reservar_espacio(request, espacio_id):
    espacio = get_object_or_404(Espacio, id=espacio_id)
    tz = get_current_timezone()  # Obtener la zona horaria actual

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        franja_horaria = request.POST.get('franja_horaria')  # Recibir la franja horaria seleccionada

        if fecha and franja_horaria:
            try:
                # Dividir la franja horaria en hora de inicio y fin
                hora_inicio, hora_fin = franja_horaria.split("-")
                fecha_inicio = make_aware(datetime.strptime(f"{fecha} {hora_inicio}", "%Y-%m-%d %H:%M"), tz)
                fecha_fin = make_aware(datetime.strptime(f"{fecha} {hora_fin}", "%Y-%m-%d %H:%M"), tz)

                # Validar que fecha_inicio < fecha_fin
                if fecha_inicio >= fecha_fin:
                    messages.error(request, "La hora de inicio debe ser anterior a la hora de fin.")
                    return render(request, 'usuarios/reservar_espacio.html', {'espacio': espacio})

                # Validar disponibilidad del espacio
                reservas = Reserva.objects.filter(
                    espacio=espacio,
                    fecha_inicio__lt=fecha_fin,
                    fecha_fin__gt=fecha_inicio
                )
                eventos = Evento.objects.filter(
                    espacio=espacio,
                    fecha_inicio__lt=fecha_fin,
                    fecha_fin__gt=fecha_inicio
                )

                if reservas.count() >= espacio.capacidad or eventos.exists():
                    messages.error(request, "La franja seleccionada no está disponible.")
                    return render(request, 'usuarios/reservar_espacio.html', {'espacio': espacio})

                # Crear la reserva
                reserva = Reserva(
                    usuario=request.user,
                    espacio=espacio,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                )
                reserva.save()

                # Actualizar el contador del usuario y redirigir
                request.user.contador += 1
                request.user.save()
                if request.user.contador == 2:
                    return redirect('valorar_app')
                else:
                    return redirect('perfil_usuario')

            except Exception as e:
                messages.error(request, f"Error al procesar la reserva: {str(e)}")

    return render(request, 'usuarios/reservar_espacio.html', {'espacio': espacio})

def bienvenido(request):
    return render(request, 'bienvenido.html')
