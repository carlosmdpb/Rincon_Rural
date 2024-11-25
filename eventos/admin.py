from django.contrib import admin
from .models import Evento

# Register your models here.
@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'espacio', 'codigo_postal']
    list_filter = ['codigo_postal']
    search_fields = ['nombre', 'codigo_postal']
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(codigo_postal=request.user.codigo_postal)
        return qs