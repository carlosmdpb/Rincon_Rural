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
import uuid

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
    # Obtener la hora actual (ajustada con el desfase necesario)
    hora_actual = now() + timedelta(hours=2)

    # Filtrar espacios por código postal del usuario
    usuario_codigo_postal = request.user.codigo_postal  # Asegúrate de que este campo exista en el modelo User
    espacios = Espacio.objects.filter(disponible=True, codigo_postal=usuario_codigo_postal)

    # Agrupar reservas activas
    reservas_activas = Reserva.objects.filter(usuario=request.user, fecha_fin__gte=hora_actual).order_by('fecha_inicio')
    reservas_activas_agrupadas = {}
    for reserva in reservas_activas:
        grupo = reserva.grupo_reserva
        if grupo not in reservas_activas_agrupadas:
            reservas_activas_agrupadas[grupo] = []
        reservas_activas_agrupadas[grupo].append(reserva)

    # Agrupar reservas pasadas
    reservas_pasadas = Reserva.objects.filter(usuario=request.user, fecha_fin__lt=hora_actual).order_by('fecha_inicio')
    reservas_pasadas_agrupadas = {}
    for reserva in reservas_pasadas:
        grupo = reserva.grupo_reserva
        if grupo not in reservas_pasadas_agrupadas:
            reservas_pasadas_agrupadas[grupo] = []
        reservas_pasadas_agrupadas[grupo].append(reserva)

    return render(request, 'usuarios/perfil.html', {
        'usuario': request.user,
        'espacios': espacios,
        'reservas_activas': reservas_activas_agrupadas,
        'reservas_pasadas': reservas_pasadas_agrupadas,
    })

@login_required
def reservar_espacio(request, espacio_id):
    espacio = get_object_or_404(Espacio, id=espacio_id)
    tz = get_current_timezone()

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        franja_horaria = request.POST.get('franja_horaria')  # Formato "HH:MM-HH:MM"

        if fecha and franja_horaria:
            try:
                # Dividir la franja seleccionada en hora de inicio y fin
                hora_inicio, hora_fin = franja_horaria.split("-")
                inicio = make_aware(datetime.strptime(f"{fecha} {hora_inicio}", "%Y-%m-%d %H:%M"), tz)
                fin = make_aware(datetime.strptime(f"{fecha} {hora_fin}", "%Y-%m-%d %H:%M"), tz)

                # Generar todas las franjas de 1 hora dentro del rango seleccionado
                franjas = []
                hora_actual = inicio
                while hora_actual < fin:
                    siguiente_hora = hora_actual + timedelta(hours=1)
                    franjas.append((hora_actual, siguiente_hora))
                    hora_actual = siguiente_hora

                # Validar y crear reservas con un mismo grupo_reserva
                grupo_reserva = uuid.uuid4()  # Generar un identificador único para el grupo
                for franja_inicio, franja_fin in franjas:
                    reservas = Reserva.objects.filter(
                        espacio=espacio,
                        fecha_inicio__lt=franja_fin,
                        fecha_fin__gt=franja_inicio
                    )
                    if reservas.count() >= espacio.capacidad:
                        raise ValueError("No hay suficiente capacidad en una de las franjas seleccionadas.")

                    # Crear la reserva
                    Reserva.objects.create(
                        usuario=request.user,
                        espacio=espacio,
                        fecha_inicio=franja_inicio,
                        fecha_fin=franja_fin,
                        grupo_reserva=grupo_reserva
                    )

                # Incrementar el contador del usuario
                request.user.contador += 1
                request.user.save()

                # Redirigir si el contador alcanza 2
                if request.user.contador == 2:
                    return redirect('valorar_app')
                else:
                    return redirect('perfil_usuario')

            except ValueError as e:
                messages.error(request, f"Error en la reserva: {str(e)}")
            except Exception as e:
                messages.error(request, f"Error al procesar la reserva: {str(e)}")

    return render(request, 'usuarios/reservar_espacio.html', {'espacio': espacio})

def bienvenido(request):
    return render(request, 'bienvenido.html')
