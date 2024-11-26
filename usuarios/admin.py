from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario
from django.contrib.auth.models import Group

class UsuarioAdmin(UserAdmin):
    # Campos que se mostrarán en la lista de usuarios
    list_display = ('username', 'email', 'dni', 'rol', 'is_active', 'is_staff', 'is_superuser', 'codigo_postal')
    list_filter = ['codigo_postal']

    def get_queryset(self, request):
        """
        Filtra los usuarios para mostrar solo aquellos que coincidan con el código postal del superusuario.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(codigo_postal=request.user.codigo_postal)
        return qs

    # Campos que se mostrarán al editar/crear un usuario
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'dni')}),  # Incluye el campo DNI
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
        ('Rol Personalizado', {'fields': ('rol',)}),  # Agregar campos personalizados aquí
        ('Código Postal', {'fields': ('codigo_postal',)}),  # Campo de solo lectura
    )

    # Campos requeridos al crear un nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'dni', 'rol', 'is_active', 'codigo_postal'),  # Incluye DNI y código postal
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        """
        Personaliza el formulario para inicializar el código postal con el del superusuario.
        """
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Solo al crear un nuevo usuario
            form.base_fields['codigo_postal'].initial = request.user.codigo_postal
            form.base_fields['codigo_postal'].widget.attrs['readonly'] = True  # Hacerlo de solo lectura
        return form

    def save_model(self, request, obj, form, change):
        """
        Asegura que el código postal se mantenga igual y tome el del superusuario al crear.
        """
        if not change:  # Solo al crear un nuevo usuario
            obj.codigo_postal = request.user.codigo_postal
        super().save_model(request, obj, form, change)

# Registrar el modelo personalizado en el administrador
admin.site.register(Usuario, UsuarioAdmin)
admin.site.unregister(Group)