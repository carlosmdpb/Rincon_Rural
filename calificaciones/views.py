from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Calificacion

@login_required
def valorar_app(request):

    if request.user.contador != 2:
        return redirect('perfil_usuario')

    if request.method == 'POST':
        puntuacion = request.POST.get('puntuacion')

        try:
            puntuacion = int(puntuacion)
            if not (1 <= puntuacion <= 5):
                raise ValueError("La valoración debe estar entre 1 y 5.")

            # Obtener o crear la instancia global de Calificacion
            calificacion, created = Calificacion.objects.get_or_create(id=1)

            # Actualizar los valores
            calificacion.puntuacion_total += puntuacion
            calificacion.numero_votos += 1
            calificacion.save()

            return redirect('perfil_usuario')

        except ValueError as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'usuarios/valorar_app.html')
