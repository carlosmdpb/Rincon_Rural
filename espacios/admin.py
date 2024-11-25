from django.contrib import admin
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import path, reverse
from .models import Espacio
from django.utils.safestring import mark_safe
from .forms import GestionarDependenciasForm

# Register your models here.

class EspacioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'capacidad', 'disponible', 'hora_apertura', 'hora_cierre', 'mostrar_dependencias', 'codigo_postal']
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
                form.save()  # Guarda las dependencias seleccionadas
                return redirect('admin:espacios_espacio_changelist')
        else:
            form = GestionarDependenciasForm(instance=espacio)

        return render(request, 'gestionar_dependencias_form.html', {
            'form': form,
            'espacio': espacio,
        })


admin.site.register(Espacio, EspacioAdmin)

