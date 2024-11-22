from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from .models import Reserva, Espacio
from .forms import ReservaForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import make_aware, get_current_timezone, now, localtime

def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user  # Asocia el usuario actual a la reserva
            reserva.save()
            messages.success(request, "Reserva creada exitosamente.")
            return redirect('listar_reservas')
        else:
            # Mostrar errores de validación
            messages.error(request, "Corrige los errores antes de continuar.")
    else:
        form = ReservaForm()

    return render(request, 'crear.html', {'form': form})

def listar_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user)
    return render(request, 'listar.html', {'reservas': reservas})

def horas_disponibles(request, espacio_id, fecha):
    try:
        # Obtener el espacio y la zona horaria actual
        espacio = get_object_or_404(Espacio, id=espacio_id)
        tz = get_current_timezone()

        # Convertir la fecha seleccionada a timezone-aware
        fecha_inicio_dia = make_aware(datetime.strptime(fecha, "%Y-%m-%d"), tz)
        fecha_fin_dia = fecha_inicio_dia + timedelta(days=1)

        # Generar todas las horas dentro del horario del espacio
        hora_actual = datetime.combine(fecha_inicio_dia.date(), espacio.hora_apertura)
        hora_cierre = datetime.combine(fecha_inicio_dia.date(), espacio.hora_cierre)

        horas_disponibles_inicio = []
        horas_disponibles_final = []

        while hora_actual < hora_cierre:
            siguiente_hora = hora_actual + timedelta(hours=1)
            horas_disponibles_inicio.append(hora_actual.strftime("%H:%M"))
            horas_disponibles_final.append(siguiente_hora.strftime("%H:%M"))
            hora_actual = siguiente_hora

        # Obtener las reservas existentes para el espacio en la fecha seleccionada
        reservas = Reserva.objects.filter(
            espacio=espacio,
            fecha_inicio__gte=fecha_inicio_dia,
            fecha_inicio__lt=fecha_fin_dia,
        )

        # Ajustar las horas de inicio para evitar conflictos
        for reserva in reservas:
            hora_inicio_reserva = reserva.fecha_inicio.astimezone(tz).time()
            hora_fin_reserva = reserva.fecha_fin.astimezone(tz).time()

            # Eliminar horas de inicio que caigan dentro de una reserva activa
            horas_disponibles_inicio = [
                hora for hora in horas_disponibles_inicio
                if not (
                    hora_inicio_reserva.strftime("%H:%M") <= hora < hora_fin_reserva.strftime("%H:%M")
                )
            ]

        # Ajustar las horas de fin dinámicamente según la hora de inicio seleccionada
        horas_disponibles_dict = {}
        for inicio in horas_disponibles_inicio:
            horas_finales_validas = []
            for fin in horas_disponibles_final:
                if fin > inicio:
                    # Comprobar conflictos con reservas activas
                    conflicto = any(
                        datetime.strptime(inicio, "%H:%M").time() < reserva.fecha_fin.time() <= datetime.strptime(fin, "%H:%M").time()
                        or datetime.strptime(fin, "%H:%M").time() > reserva.fecha_inicio.time() >= datetime.strptime(inicio, "%H:%M").time()
                        for reserva in reservas
                    )
                    if not conflicto:
                        horas_finales_validas.append(fin)

            horas_disponibles_dict[inicio] = horas_finales_validas

        return JsonResponse({"horas_disponibles": horas_disponibles_dict})

    except Espacio.DoesNotExist:
        return JsonResponse({"error": "Espacio no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
