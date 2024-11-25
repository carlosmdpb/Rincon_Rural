from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario
from django.contrib.auth.models import Group

# Register your models here.
class UsuarioAdmin(UserAdmin):
    # Campos que se mostrarán en la lista de usuarios
    list_display = ('username', 'email', 'dni', 'rol', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ['codigo_postal']

    def get_queryset(self, request):
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
        ('Código Postal', {'fields': ('codigo_postal',)}),
    )
    
    # Campos requeridos al crear un nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'dni', 'rol', 'is_active'),  # Incluye DNI aquí
        }),
    )
    
    # Campos por los que se puede buscar
    search_fields = ('username', 'email', 'dni', 'first_name', 'last_name')  # Añade búsqueda por DNI
    ordering = ('username',)

# Registrar el modelo personalizado en el administrador
admin.site.register(Usuario, UsuarioAdmin)
admin.site.unregister(Group)
