from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from .models import Reserva, Espacio
from eventos.models import Evento
from .forms import ReservaForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import make_aware, get_current_timezone, now
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            
            # Convertir fechas a timezone-aware si son necesarias
            tz = get_current_timezone()
            reserva.fecha_inicio = make_aware(reserva.fecha_inicio, tz)
            reserva.fecha_fin = make_aware(reserva.fecha_fin, tz)
            
            reserva.save()
            messages.success(request, "Reserva creada exitosamente.")
            return redirect('listar_reservas')
        else:
            messages.error(request, "Corrige los errores antes de continuar.")
    else:
        form = ReservaForm()

    return render(request, 'crear.html', {'form': form})

@login_required
def listar_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user)
    reservas = Reserva.objects.filter(codigo_postal=request.user.codigo_postal)
    return render(request, 'listar.html', {'reservas': reservas})

def horas_disponibles(request, espacio_id, fecha):
    try:
        espacio = get_object_or_404(Espacio, id=espacio_id)
        tz = get_current_timezone()

        espacios_afectados = list(espacio.dependencias.all()) + [espacio]

        # Obtener la duración de la reserva deseada (en horas o día entero)
        duracion_horas = request.GET.get("duracion", "1")
        if duracion_horas == "dia":
            duracion_horas = None
        else:
            duracion_horas = int(duracion_horas)

        ahora = now().astimezone(tz)
        fecha_seleccionada = datetime.strptime(fecha, "%Y-%m-%d").date()

        fecha_inicio_dia = make_aware(datetime.combine(fecha_seleccionada, espacio.hora_apertura), tz)
        fecha_fin_dia = make_aware(datetime.combine(fecha_seleccionada, espacio.hora_cierre), tz)

        # Si es hoy, excluir franjas pasadas
        if fecha_seleccionada == ahora.date():
            hora_actual_minima = ahora.replace(minute=0, second=0, microsecond=0)
            if ahora.minute > 0:
                hora_actual_minima += timedelta(hours=1)
            fecha_inicio_dia = max(fecha_inicio_dia, hora_actual_minima)

        # Generar franjas de 1 hora (internas)
        franjas_horas = []
        hora_actual = fecha_inicio_dia
        while hora_actual < fecha_fin_dia:
            siguiente_hora = hora_actual + timedelta(hours=1)
            franjas_horas.append((hora_actual, siguiente_hora))
            hora_actual = siguiente_hora

        # Obtener todas las reservas y eventos para el día seleccionado
        reservas = Reserva.objects.filter(
            espacio__in=espacios_afectados,
            fecha_inicio__lt=fecha_fin_dia,
            fecha_fin__gt=fecha_inicio_dia,
        )
        eventos = Evento.objects.filter(
            espacio__in=espacios_afectados,
            fecha_inicio__lt=fecha_fin_dia,
            fecha_fin__gt=fecha_inicio_dia,
        )

        # Verificar disponibilidad de cada franja de 1 hora
        franjas_disponibles_horas = []
        for inicio, fin in franjas_horas:
            reservas_en_franja = reservas.filter(fecha_inicio__lt=fin, fecha_fin__gt=inicio)
            eventos_en_franja = eventos.filter(fecha_inicio__lt=fin, fecha_fin__gt=inicio)

            if reservas_en_franja.count() < espacio.capacidad and not eventos_en_franja.exists():
                franjas_disponibles_horas.append((inicio, fin))

        # Generar franjas largas según la duración seleccionada
        franjas_disponibles = []
        if duracion_horas is None:
            # Día entero: una sola franja
            if len(franjas_disponibles_horas) == len(franjas_horas):  # Si todas las horas están disponibles
                franjas_disponibles.append((fecha_inicio_dia.strftime("%H:%M"), fecha_fin_dia.strftime("%H:%M")))
        else:
            # Franjas dinámicas según la duración seleccionada
            for i in range(len(franjas_disponibles_horas)):
                # Comprobar si hay suficientes horas consecutivas disponibles
                franja_inicio = franjas_disponibles_horas[i][0]
                franja_fin = franja_inicio + timedelta(hours=duracion_horas)

                # Validar que todas las horas dentro del rango estén disponibles
                horas_validas = [
                    (inicio, fin)
                    for inicio, fin in franjas_disponibles_horas
                    if inicio >= franja_inicio and fin <= franja_fin
                ]

                if len(horas_validas) == duracion_horas:
                    franjas_disponibles.append(
                        (franja_inicio.strftime("%H:%M"), franja_fin.strftime("%H:%M"))
                    )

        return JsonResponse({"franjas_disponibles": franjas_disponibles})

    except Espacio.DoesNotExist:
        return JsonResponse({"error": "Espacio no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def dias_no_disponibles(request, espacio_id):
    try:
        espacio = get_object_or_404(Espacio, id=espacio_id)
        tz = get_current_timezone()
        dias_no_disponibles = []

        # Obtener espacios afectados (espacio y sus dependencias)
        espacios_afectados = list(espacio.dependencias.all()) + [espacio]

        # Analizar los próximos 30 días
        fecha_actual = now().astimezone(tz)
        for i in range(90):  # Revisar los próximos 30 días
            fecha = fecha_actual.date() + timedelta(days=i)
            fecha_inicio_dia = make_aware(datetime.combine(fecha, espacio.hora_apertura), tz)
            fecha_fin_dia = make_aware(datetime.combine(fecha, espacio.hora_cierre), tz)

            # Bloquear el día actual si todas las franjas han pasado
            if fecha == fecha_actual.date() and fecha_inicio_dia < fecha_actual >= fecha_fin_dia:
                dias_no_disponibles.append(fecha.strftime("%Y-%m-%d"))
                continue

            # Buscar eventos y reservas para espacios afectados
            eventos = Evento.objects.filter(
                espacio__in=espacios_afectados,
                fecha_inicio__lt=fecha_fin_dia,
                fecha_fin__gt=fecha_inicio_dia,
            )
            reservas = Reserva.objects.filter(
                espacio__in=espacios_afectados,
                fecha_inicio__lt=fecha_fin_dia,
                fecha_fin__gt=fecha_inicio_dia,
            )

            # Bloquear día completo si hay eventos que cubren todo el horario del espacio
            if eventos.filter(fecha_inicio__lte=fecha_inicio_dia, fecha_fin__gte=fecha_fin_dia).exists():
                dias_no_disponibles.append(fecha.strftime("%Y-%m-%d"))
                continue

            # Verificar disponibilidad por franjas horarias
            dia_bloqueado = True
            hora_actual = max(fecha_actual, fecha_inicio_dia) if fecha == fecha_actual.date() else fecha_inicio_dia

            while hora_actual < fecha_fin_dia:
                siguiente_hora = hora_actual + timedelta(hours=1)
                reservas_en_franja = reservas.filter(fecha_inicio__lt=siguiente_hora, fecha_fin__gt=hora_actual)
                eventos_en_franja = eventos.filter(fecha_inicio__lt=siguiente_hora, fecha_fin__gt=hora_actual)

                if reservas_en_franja.count() < espacio.capacidad and not eventos_en_franja.exists():
                    dia_bloqueado = False
                    break

                hora_actual = siguiente_hora

            if dia_bloqueado:
                dias_no_disponibles.append(fecha.strftime("%Y-%m-%d"))

        return JsonResponse({"dias_no_disponibles": dias_no_disponibles})

    except Espacio.DoesNotExist:
        return JsonResponse({"error": "Espacio no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    if request.method == 'POST':
        reserva.delete()
        return redirect('perfil_usuario')
    return render(request, 'cancelar_reserva.html', {'reserva': reserva})

@login_required
@require_POST
def cancelar_reserva_grupo(request, grupo_reserva):
    reservas = Reserva.objects.filter(grupo_reserva=grupo_reserva, usuario=request.user)
    if reservas.exists():
        reservas.delete()
        return redirect('perfil_usuario')
    return JsonResponse({"error": "Reserva no encontrada"}, status=404)