from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from .models import Reserva, Espacio
from eventos.models import Evento
from .forms import ReservaForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import make_aware, get_current_timezone, now
from django.contrib.auth.decorators import login_required

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

        # Obtener la duración de la reserva deseada (en horas o día entero)
        duracion_horas = request.GET.get("duracion", "1")

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

        # Caso especial: día entero
        if duracion_horas == "dia":
            franjas = [(fecha_inicio_dia, fecha_fin_dia)]
        else:
            duracion_horas = int(duracion_horas)
            franjas = []
            hora_actual = fecha_inicio_dia
            while hora_actual + timedelta(hours=duracion_horas) <= fecha_fin_dia:
                siguiente_hora = hora_actual + timedelta(hours=duracion_horas)
                franjas.append((hora_actual, siguiente_hora))
                hora_actual += timedelta(hours=1)

        # Verificar disponibilidad por franja
        reservas = Reserva.objects.filter(
            espacio=espacio,
            fecha_inicio__lt=fecha_fin_dia,
            fecha_fin__gt=fecha_inicio_dia,
        )
        eventos = Evento.objects.filter(
            espacio=espacio,
            fecha_inicio__lt=fecha_fin_dia,
            fecha_fin__gt=fecha_inicio_dia,
        )

        franjas_disponibles = []
        for inicio, fin in franjas:
            reservas_en_franja = reservas.filter(fecha_inicio__lt=fin, fecha_fin__gt=inicio)
            eventos_en_franja = eventos.filter(fecha_inicio__lt=fin, fecha_fin__gt=inicio)

            # Si la franja está disponible, agregarla
            if reservas_en_franja.count() < espacio.capacidad and not eventos_en_franja.exists():
                franjas_disponibles.append((inicio.strftime("%H:%M"), fin.strftime("%H:%M")))

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

        # Analizar los próximos 30 días
        fecha_actual = now().astimezone(tz).date()
        for i in range(30):  # Revisar los próximos 30 días
            fecha = fecha_actual + timedelta(days=i)
            fecha_inicio_dia = make_aware(datetime.combine(fecha, espacio.hora_apertura), tz)
            fecha_fin_dia = make_aware(datetime.combine(fecha, espacio.hora_cierre), tz)

            # Generar franjas horarias del día
            franjas = []
            hora_actual = fecha_inicio_dia

            # Si es hoy, ajustar para excluir franjas pasadas
            if fecha == fecha_actual:
                hora_actual = now().astimezone(tz).replace(minute=0, second=0, microsecond=0)
                if now().minute > 0:
                    hora_actual += timedelta(hours=1)

            while hora_actual < fecha_fin_dia:
                siguiente_hora = hora_actual + timedelta(hours=1)
                franjas.append((hora_actual, siguiente_hora))
                hora_actual = siguiente_hora

            # Verificar disponibilidad de cada franja
            reservas = Reserva.objects.filter(
                espacio=espacio,
                fecha_inicio__lt=fecha_fin_dia,
                fecha_fin__gt=fecha_inicio_dia,
            )
            eventos = Evento.objects.filter(
                espacio=espacio,
                fecha_inicio__lt=fecha_fin_dia,
                fecha_fin__gt=fecha_inicio_dia,
            )

            dia_disponible = False
            for inicio, fin in franjas:
                reservas_en_franja = reservas.filter(fecha_inicio__lt=fin, fecha_fin__gt=inicio)
                eventos_en_franja = eventos.filter(fecha_inicio__lt=fin, fecha_fin__gt=inicio)

                # Si hay una franja disponible, el día es válido
                if reservas_en_franja.count() < espacio.capacidad and not eventos_en_franja.exists():
                    dia_disponible = True
                    break

            # Si no hay ninguna franja disponible, el día está bloqueado
            if not dia_disponible:
                dias_no_disponibles.append(fecha.strftime("%Y-%m-%d"))

        return JsonResponse({"dias_no_disponibles": dias_no_disponibles})

    except Espacio.DoesNotExist:
        return JsonResponse({"error": "Espacio no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    if request.method == 'POST':
        reserva.delete()
        return redirect('perfil_usuario')
    return render(request, 'cancelar_reserva.html', {'reserva': reserva})