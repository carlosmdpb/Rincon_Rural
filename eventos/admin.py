from django.contrib import admin
from .models import Evento

# Register your models here.
@admin.register(Evento)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'espacio', 'fecha_inicio', 'fecha_fin')  # Campos visibles en la tabla
    list_filter = ('espacio', 'fecha_inicio')  # Filtros en la barra lateral
    search_fields = ('nombre', 'descripcion')