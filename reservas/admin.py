from django.contrib import admin
from .models import Reserva

# Register your models here.

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'espacio', 'fecha_inicio', 'fecha_fin', 'estado')  # Campos visibles en la tabla
    list_filter = ('estado', 'espacio')  # Filtros en la barra lateral
    search_fields = ('usuario__username', 'espacio__nombre')  # Campos para la barra de búsqueda
