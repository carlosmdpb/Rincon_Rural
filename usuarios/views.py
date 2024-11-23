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
from django.contrib.messages import get_messages
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils.timezone import make_aware, get_current_timezone
from datetime import datetime

# Vista para el registro de usuarios
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_active = False  # Usuario inactivo hasta que sea aprobado
            usuario.save()
            # Agregar el mensaje de éxito y redirigir al login
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

    # Eliminar mensajes residuales al cargar la página
    storage = get_messages(request)
    for _ in storage:
        pass  # Limpia los mensajes de la sesión actual

    return render(request, 'usuarios/registro.html', {'form': form})

# Vista genérica para el inicio de sesión
class LoginUsuario(LoginView):
    template_name = 'usuarios/login.html'

    def form_invalid(self, form):
        # Evita que Django añada el mensaje por defecto
        form.errors.clear()

        # Obtener los datos del formulario
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')

        # Intentar encontrar al usuario
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                # Usuario encontrado pero inactivo
                messages.error(
                    self.request,
                    "El administrador tiene que aprobar tu solicitud de registro. "
                    "Manténgase a la espera. Gracias por su paciencia."
                )
            elif not check_password(password, user.password):
                # Contraseña incorrecta
                messages.error(
                    self.request,
                    "Por favor, introduce una contraseña correcta. "
                    "Ambos campos pueden distinguir entre mayúsculas y minúsculas."
                )
            else:
                # Si llegamos aquí, algo inesperado falló (este bloque no debería ejecutarse normalmente)
                messages.error(
                    self.request,
                    "Ocurrió un error inesperado. Por favor, inténtalo nuevamente."
                )
        except User.DoesNotExist:
            # Usuario no encontrado
            messages.error(
                self.request,
                "El nombre de usuario o la contraseña son incorrectos."
            )

        # Retornar el formulario con los mensajes personalizados
        return self.render_to_response(self.get_context_data(form=form))

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
    tz = get_current_timezone()  # Obtener la zona horaria actual

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')

        if fecha and hora_inicio and hora_fin:
            try:
                # Combinar fecha y hora y convertirlas en timezone-aware
                fecha_inicio = make_aware(datetime.strptime(f"{fecha} {hora_inicio}", "%Y-%m-%d %H:%M"), tz)
                fecha_fin = make_aware(datetime.strptime(f"{fecha} {hora_fin}", "%Y-%m-%d %H:%M"), tz)

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
