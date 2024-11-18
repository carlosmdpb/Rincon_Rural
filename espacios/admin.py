from django.contrib import admin
from .models import Espacio

# Register your models here.
@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad', 'disponible')
    list_filter = ('disponible', 'capacidad')
    search_fields = ('nombre', 'disponible')