from django.contrib import admin
from .models import Reserva
from usuarios.models import Usuario
from espacios.models import Espacio

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'espacio', 'fecha_inicio', 'fecha_fin', 'estado', 'codigo_postal', 'autorizada')
    list_filter = ['codigo_postal']
    search_fields = ['usuario__username', 'codigo_postal']
    actions = ['autorizar_reservas']

    def autorizar_reservas(self, request, queryset):
        """
        Acción para autorizar reservas seleccionadas.
        """
        queryset.update(autorizada=True)
        self.message_user(request, f"{queryset.count()} reservas autorizadas.")
    
    autorizar_reservas.short_description = "Autorizar reservas seleccionadas"

    def get_queryset(self, request):
        """
        Filtra las reservas para mostrar solo aquellas que coincidan con el código postal del superusuario.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(codigo_postal=request.user.codigo_postal)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        """
        Personaliza el formulario para inicializar 'codigo_postal' y filtrar los campos 'usuario' y 'espacio'.
        """
        form = super().get_form(request, obj, **kwargs)

        # Inicializar el código postal con el del superusuario si se está creando una nueva reserva
        if not obj:  # Solo al crear una nueva reserva
            form.base_fields['codigo_postal'].initial = request.user.codigo_postal
            form.base_fields['codigo_postal'].widget.attrs['readonly'] = True  # Hacerlo de solo lectura

        # Filtrar el campo 'usuario' para mostrar solo usuarios con el mismo código postal
        if 'usuario' in form.base_fields:
            form.base_fields['usuario'].queryset = Usuario.objects.filter(
                codigo_postal=request.user.codigo_postal
            )

        # Filtrar el campo 'espacio' para mostrar solo espacios con el mismo código postal
        if 'espacio' in form.base_fields:
            form.base_fields['espacio'].queryset = Espacio.objects.filter(
                codigo_postal=request.user.codigo_postal
            )

        return form

    def save_model(self, request, obj, form, change):
        """
        Asegura que el código postal se mantenga igual y tome el del superusuario al crear.
        """
        if not change:  # Solo al crear una nueva reserva
            obj.codigo_postal = request.user.codigo_postal
        super().save_model(request, obj, form, change)