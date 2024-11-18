from django.shortcuts import render
from .models import Evento

# Create your views here.
def listar_eventos(request):
    eventos = Evento.objects.all()
    return render(request, 'eventos/listar.html', {'eventos': eventos})