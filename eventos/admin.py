from django.contrib import admin
from .models import Evento
from espacios.models import Espacio

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'espacio', 'codigo_postal']
    list_filter = ['codigo_postal']
    search_fields = ['nombre', 'codigo_postal']

    def get_queryset(self, request):
        """
        Filtra los eventos para mostrar solo aquellos que coincidan con el código postal del superusuario.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(codigo_postal=request.user.codigo_postal)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        """
        Personaliza el formulario para inicializar 'codigo_postal' y filtrar el campo 'espacio' por el código postal.
        """
        form = super().get_form(request, obj, **kwargs)

        # Inicializar el código postal con el del superusuario si se está creando un nuevo evento
        if not obj:  # Solo al crear un nuevo evento
            form.base_fields['codigo_postal'].initial = request.user.codigo_postal
            form.base_fields['codigo_postal'].widget.attrs['readonly'] = True  # Hacerlo de solo lectura

        # Filtrar el campo 'espacio' para mostrar solo los espacios del mismo código postal
        if 'espacio' in form.base_fields:
            form.base_fields['espacio'].queryset = Espacio.objects.filter(
                codigo_postal=request.user.codigo_postal
            )

        return form

    def save_model(self, request, obj, form, change):
        """
        Asegura que el código postal se mantenga igual y tome el del superusuario al crear.
        """
        if not change:  # Solo al crear un nuevo evento
            obj.codigo_postal = request.user.codigo_postal
        super().save_model(request, obj, form, change)
