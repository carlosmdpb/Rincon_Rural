from django.contrib import admin
from .models import Reserva

# Register your models here.

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'espacio', 'fecha_inicio', 'fecha_fin', 'estado', 'codigo_postal')
    list_filter = ['codigo_postal']
    search_fields = ['usuario__username', 'codigo_postal']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(codigo_postal=request.user.codigo_postal)
        return qs
