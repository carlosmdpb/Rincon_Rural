from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from .models import Reserva, Espacio
from .forms import ReservaForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import make_aware, get_current_timezone, now

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
        fecha_actual = now().astimezone(tz)

        # Convertir la fecha seleccionada a timezone-aware
        fecha_inicio_dia = make_aware(datetime.strptime(fecha, "%Y-%m-%d"), tz)
        fecha_fin_dia = fecha_inicio_dia + timedelta(days=1)

        # Generar todas las horas disponibles dentro del horario del espacio
        hora_actual = make_aware(datetime.combine(fecha_inicio_dia.date(), espacio.hora_apertura), tz)
        hora_cierre = make_aware(datetime.combine(fecha_inicio_dia.date(), espacio.hora_cierre), tz)
        horas_inicio = []
        horas_fin = []

        while hora_actual < hora_cierre:
            if hora_actual > fecha_actual:
                horas_inicio.append(hora_actual.strftime("%H:%M"))
            hora_actual += timedelta(hours=1)

        hora_actual = make_aware(datetime.combine(fecha_inicio_dia.date(), espacio.hora_apertura), tz)
        while hora_actual <= hora_cierre:
            if hora_actual > fecha_actual:
                horas_fin.append(hora_actual.strftime("%H:%M"))
            hora_actual += timedelta(hours=1)

        # Excluir horas que interfieran con reservas existentes
        reservas = Reserva.objects.filter(
            espacio=espacio,
            fecha_inicio__gte=fecha_inicio_dia,
            fecha_inicio__lt=fecha_fin_dia,
        )

        for reserva in reservas:
            hora_inicio_reserva = reserva.fecha_inicio.astimezone(tz).time()
            hora_fin_reserva = reserva.fecha_fin.astimezone(tz).time()
            horas_inicio = [
                hora for hora in horas_inicio
                if datetime.strptime(hora, "%H:%M").time() >= hora_fin_reserva or datetime.strptime(hora, "%H:%M").time() < hora_inicio_reserva
            ]
            horas_fin = [
                hora for hora in horas_fin
                if datetime.strptime(hora, "%H:%M").time() > hora_inicio_reserva
            ]

        return JsonResponse({"horas_inicio": horas_inicio, "horas_fin": horas_fin})

    except Espacio.DoesNotExist:
        return JsonResponse({"error": "Espacio no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)