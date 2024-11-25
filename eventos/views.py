from django.shortcuts import render
from .models import Evento
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def listar_eventos(request):
    eventos = Evento.objects.all()
    eventos = Evento.objects.filter(codigo_postal=request.user.codigo_postal)
    return render(request, 'eventos/listar.html', {'eventos': eventos})