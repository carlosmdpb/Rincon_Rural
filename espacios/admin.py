from django.contrib import admin
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import path, reverse
from .models import Espacio
from django.utils.safestring import mark_safe
from .forms import GestionarDependenciasForm

class EspacioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'capacidad', 'disponible', 'autorizacion', 'hora_apertura', 'hora_cierre', 'mostrar_dependencias', 'codigo_postal']
    list_filter = ['codigo_postal']
    search_fields = ['nombre', 'codigo_postal']

    def get_queryset(self, request):
        """
        Filtra los espacios para mostrar solo aquellos que coincidan con el código postal del superusuario.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(codigo_postal=request.user.codigo_postal)
        return qs
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Personaliza el formulario de administración para inicializar 'codigo_postal' y filtrar dependencias.
        """
        form = super().get_form(request, obj, **kwargs)
        
        # Inicializar el código postal con el del superusuario si se está creando un nuevo espacio
        if not obj:  # Solo al crear un nuevo espacio
            form.base_fields['codigo_postal'].initial = request.user.codigo_postal
            form.base_fields['codigo_postal'].widget.attrs['readonly'] = True  # Hacerlo de solo lectura
        
        # Filtrar dependencias si el campo existe en el formulario
        if 'dependencias' in form.base_fields:
            form.base_fields['dependencias'].queryset = Espacio.objects.filter(
                codigo_postal=request.user.codigo_postal
            )
        return form

    def save_model(self, request, obj, form, change):
        """
        Asegura que el código postal se mantenga igual y tome el del superusuario al crear.
        """
        if not change:  # Solo al crear un nuevo espacio
            obj.codigo_postal = request.user.codigo_postal
        super().save_model(request, obj, form, change)

    def mostrar_dependencias(self, obj):
        """
        Devuelve una lista de nombres de los espacios dependientes.
        """
        return ", ".join([dependencia.nombre for dependencia in obj.dependencias.all()])

    mostrar_dependencias.short_description = "Dependencias"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Personaliza la vista de edición para insertar enlaces y configuraciones adicionales.
        """
        extra_context = extra_context or {}

        # Solo genera la URL si el objeto existe
        try:
            extra_context['gestionar_dependencias_url'] = reverse('admin:gestionar_dependencias', args=[object_id])
        except Espacio.DoesNotExist:
            extra_context['gestionar_dependencias_url'] = None

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        """
        Define rutas adicionales en el administrador para gestionar dependencias.
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                'espacio/<int:object_id>/dependencias/',
                self.admin_site.admin_view(self.gestionar_dependencias_view),
                name='gestionar_dependencias',
            ),
        ]
        return custom_urls + urls

    def gestionar_dependencias_view(self, request, object_id):
        """
        Vista para gestionar las dependencias de un espacio.
        """
        espacio = get_object_or_404(Espacio, id=object_id)

        if request.method == 'POST':
            form = GestionarDependenciasForm(request.POST, instance=espacio)
            if form.is_valid():
                form.save()
                return redirect('admin:espacios_espacio_changelist')
        else:
            form = GestionarDependenciasForm(instance=espacio)

        # Filtrar dependencias solo para superusuarios
        if request.user.is_superuser:
            form.fields['dependencias'].queryset = Espacio.objects.filter(
                codigo_postal=request.user.codigo_postal
            ).exclude(id=espacio.id)  # Excluir el propio espacio para evitar auto-dependencias

        return render(request, 'gestionar_dependencias_form.html', {
            'form': form,
            'espacio': espacio,
        })

admin.site.register(Espacio, EspacioAdmin)