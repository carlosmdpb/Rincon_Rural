from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from .models import Reserva, Espacio
from .forms import ReservaForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import make_aware
from django.utils.timezone import make_aware, get_current_timezone

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

        # Generar todas las parejas de horas dentro del horario del espacio
        hora_actual = make_aware(datetime.combine(fecha_inicio_dia.date(), espacio.hora_apertura), tz)
        hora_cierre = make_aware(datetime.combine(fecha_inicio_dia.date(), espacio.hora_cierre), tz)
        parejas_horas = []

        while hora_actual + timedelta(hours=1) <= hora_cierre:
            pareja = (
                hora_actual.strftime("%H:%M"),
                (hora_actual + timedelta(hours=1)).strftime("%H:%M"),
            )
            parejas_horas.append(pareja)
            hora_actual += timedelta(hours=1)

        # Excluir parejas que interfieran con reservas existentes
        reservas = Reserva.objects.filter(
            espacio=espacio,
            fecha_inicio__gte=fecha_inicio_dia,
            fecha_inicio__lt=fecha_fin_dia,
        )

        for reserva in reservas:
            hora_inicio_reserva = reserva.fecha_inicio.astimezone(tz).time()
            hora_fin_reserva = reserva.fecha_fin.astimezone(tz).time()
            parejas_horas = [
                pareja
                for pareja in parejas_horas
                if not (
                    hora_inicio_reserva <= datetime.strptime(pareja[0], "%H:%M").time() < hora_fin_reserva
                    or hora_inicio_reserva < datetime.strptime(pareja[1], "%H:%M").time() <= hora_fin_reserva
                )
            ]

        return JsonResponse({"horas_disponibles": parejas_horas})

    except Espacio.DoesNotExist:
        return JsonResponse({"error": "Espacio no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


