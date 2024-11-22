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
        ahora = now().astimezone(tz)  # Fecha y hora actuales con zona horaria

        # Convertir la fecha seleccionada a datetime.date
        fecha_seleccionada = datetime.strptime(fecha, "%Y-%m-%d").date()

        # Horario del espacio para la fecha seleccionada
        fecha_inicio_dia = make_aware(datetime.combine(fecha_seleccionada, espacio.hora_apertura), tz)
        fecha_fin_dia = make_aware(datetime.combine(fecha_seleccionada, espacio.hora_cierre), tz)

        horas_disponibles_inicio = []
        horas_disponibles_fin = []

        # Generar horas disponibles
        hora_actual = fecha_inicio_dia
        while hora_actual < fecha_fin_dia:
            siguiente_hora = hora_actual + timedelta(hours=1)

            # Si es el día de hoy, excluir horas pasadas
            if fecha_seleccionada > ahora.date() or hora_actual >= ahora:
                horas_disponibles_inicio.append(hora_actual.strftime("%H:%M"))
                horas_disponibles_fin.append(siguiente_hora.strftime("%H:%M"))

            hora_actual = siguiente_hora

        # Obtener las reservas existentes para el espacio en la fecha seleccionada
        reservas = Reserva.objects.filter(
            espacio=espacio,
            fecha_inicio__date=fecha_seleccionada
        )

        # Ajustar las horas de inicio para evitar conflictos
        for reserva in reservas:
            reserva_inicio = reserva.fecha_inicio.astimezone(tz).time()
            reserva_fin = reserva.fecha_fin.astimezone(tz).time()

            # Eliminar horas de inicio que caigan dentro de una reserva activa
            horas_disponibles_inicio = [
                hora for hora in horas_disponibles_inicio
                if not (reserva_inicio.strftime("%H:%M") <= hora < reserva_fin.strftime("%H:%M"))
            ]

        # Ajustar las horas de fin dinámicamente según la hora de inicio seleccionada
        horas_disponibles_dict = {}
        for inicio in horas_disponibles_inicio:
            horas_finales_validas = []
            for fin in horas_disponibles_fin:
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

    
def dias_no_disponibles(request, espacio_id):
    try:
        espacio = get_object_or_404(Espacio, id=espacio_id)
        tz = get_current_timezone()
        fecha_actual = now().astimezone(tz).date()
        hora_actual = now().astimezone(tz).time()
        dias_no_disponibles = []

        # Analizar los próximos 30 días
        for i in range(30):  # Por ejemplo, 30 días futuros
            fecha = fecha_actual + timedelta(days=i)
            fecha_inicio_dia = make_aware(datetime.combine(fecha, datetime.min.time()), tz)
            fecha_fin_dia = make_aware(datetime.combine(fecha, datetime.max.time()), tz)

            # Generar todas las horas posibles del día
            hora_actual_dia = make_aware(datetime.combine(fecha, espacio.hora_apertura), tz)
            hora_cierre = make_aware(datetime.combine(fecha, espacio.hora_cierre), tz)
            horas_disponibles = []

            while hora_actual_dia < hora_cierre:
                if fecha > fecha_actual or hora_actual_dia.time() > hora_actual:
                    horas_disponibles.append(hora_actual_dia.strftime("%H:%M"))
                hora_actual_dia += timedelta(hours=1)

            # Excluir horas ocupadas
            reservas = Reserva.objects.filter(
                espacio=espacio,
                fecha_inicio__gte=fecha_inicio_dia,
                fecha_inicio__lt=fecha_fin_dia,
            )
            for reserva in reservas:
                hora_inicio_reserva = reserva.fecha_inicio.astimezone(tz).time()
                hora_fin_reserva = reserva.fecha_fin.astimezone(tz).time()
                horas_disponibles = [
                    hora
                    for hora in horas_disponibles
                    if not (hora_inicio_reserva <= datetime.strptime(hora, "%H:%M").time() < hora_fin_reserva)
                ]

            # Si no hay horas disponibles, deshabilitar el día
            if not horas_disponibles:
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
        messages.success(request, 'Reserva cancelada con éxito.')
        return redirect('perfil_usuario')
    return render(request, 'cancelar_reserva.html', {'reserva': reserva})

def editar_reserva(request, reserva_id):
    # Obtener la reserva existente
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == 'POST':
        print(request.POST)  # Depuración: imprime los datos enviados

        # Capturar los datos del formulario manualmente
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')

        try:
            # Validar que todos los campos necesarios están presentes
            if not all([fecha, hora_inicio, hora_fin]):
                messages.error(request, "Faltan datos en el formulario.")
                return redirect('editar_reserva', reserva_id=reserva.id)

            # Convertir los datos en objetos datetime
            fecha_inicio = datetime.strptime(f"{fecha} {hora_inicio}", "%Y-%m-%d %H:%M")
            fecha_fin = datetime.strptime(f"{fecha} {hora_fin}", "%Y-%m-%d %H:%M")

            # Actualizar la reserva
            reserva.fecha_inicio = fecha_inicio
            reserva.fecha_fin = fecha_fin
            reserva.save()

            messages.success(request, "Reserva actualizada correctamente.")
            return redirect('perfil_usuario')

        except Exception as e:
            print(f"Error al actualizar la reserva: {e}")  # Imprime el error para depuración
            messages.error(request, "Ocurrió un error al actualizar la reserva. Por favor, intenta nuevamente.")

    # Cargar los datos actuales de la reserva en el formulario para el método GET
    return render(request, 'editar_reserva.html', {
        'reserva': reserva,
        'espacio': reserva.espacio,  # Si necesitas el espacio en la plantilla
    })

def horas_disponibles_editar(request, espacio_id, fecha, reserva_id):
    try:
        espacio = get_object_or_404(Espacio, id=espacio_id)
        reserva_actual = get_object_or_404(Reserva, id=reserva_id)
        tz = get_current_timezone()

        ahora = now().astimezone(tz)
        fecha_seleccionada = datetime.strptime(fecha, "%Y-%m-%d").date()

        fecha_inicio_dia = make_aware(datetime.combine(fecha_seleccionada, espacio.hora_apertura), tz)
        fecha_fin_dia = make_aware(datetime.combine(fecha_seleccionada, espacio.hora_cierre), tz)

        horas_disponibles_inicio = []
        horas_disponibles_fin = []

        hora_actual = fecha_inicio_dia
        while hora_actual < fecha_fin_dia:
            siguiente_hora = hora_actual + timedelta(hours=1)
            if fecha_seleccionada > ahora.date() or hora_actual >= ahora:
                horas_disponibles_inicio.append(hora_actual.strftime("%H:%M"))
                horas_disponibles_fin.append(siguiente_hora.strftime("%H:%M"))
            hora_actual = siguiente_hora

        reservas = Reserva.objects.filter(
            espacio=espacio,
            fecha_inicio__date=fecha_seleccionada
        ).exclude(id=reserva_actual.id)

        for reserva in reservas:
            reserva_inicio = reserva.fecha_inicio.astimezone(tz).time()
            reserva_fin = reserva.fecha_fin.astimezone(tz).time()

            horas_disponibles_inicio = [
                hora for hora in horas_disponibles_inicio
                if not (reserva_inicio.strftime("%H:%M") <= hora < reserva_fin.strftime("%H:%M"))
            ]

        horas_disponibles_dict = {}
        for inicio in horas_disponibles_inicio:
            horas_finales_validas = []
            for fin in horas_disponibles_fin:
                if fin > inicio:
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

def dias_no_disponibles_editar(request, espacio_id, reserva_id):
    try:
        espacio = get_object_or_404(Espacio, id=espacio_id)
        tz = get_current_timezone()
        fecha_actual = now().astimezone(tz).date()
        hora_actual = now().astimezone(tz).time()  # Hora actual con zona horaria
        dias_no_disponibles = []

        # Obtener la reserva que se está editando
        reserva_actual = get_object_or_404(Reserva, id=reserva_id)

        # Analizar los próximos 30 días
        for i in range(30):
            fecha = fecha_actual + timedelta(days=i)
            fecha_inicio_dia = make_aware(datetime.combine(fecha, datetime.min.time()), tz)
            fecha_fin_dia = make_aware(datetime.combine(fecha, datetime.max.time()), tz)

            # Generar todas las horas posibles del día
            hora_actual_calendario = make_aware(datetime.combine(fecha, espacio.hora_apertura), tz)
            hora_cierre = make_aware(datetime.combine(fecha, espacio.hora_cierre), tz)
            horas_disponibles = []

            # Verificar si el día actual ya no tiene horas disponibles
            if fecha == fecha_actual and hora_actual >= espacio.hora_cierre:
                dias_no_disponibles.append(fecha.strftime("%Y-%m-%d"))
                continue

            while hora_actual_calendario < hora_cierre:
                horas_disponibles.append(hora_actual_calendario.strftime("%H:%M"))
                hora_actual_calendario += timedelta(hours=1)

            # Filtrar horas ocupadas, excluyendo la reserva actual
            reservas = Reserva.objects.filter(
                espacio=espacio,
                fecha_inicio__gte=fecha_inicio_dia,
                fecha_inicio__lt=fecha_fin_dia,
            ).exclude(id=reserva_id)

            for reserva in reservas:
                hora_inicio_reserva = reserva.fecha_inicio.astimezone(tz).time()
                hora_fin_reserva = reserva.fecha_fin.astimezone(tz).time()
                horas_disponibles = [
                    hora
                    for hora in horas_disponibles
                    if not (hora_inicio_reserva <= datetime.strptime(hora, "%H:%M").time() < hora_fin_reserva)
                ]

            # Si no hay horas disponibles (excluyendo la reserva actual), deshabilitar el día
            if not horas_disponibles:
                dias_no_disponibles.append(fecha.strftime("%Y-%m-%d"))

        return JsonResponse({"dias_no_disponibles": dias_no_disponibles})

    except Espacio.DoesNotExist:
        return JsonResponse({"error": "Espacio no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)