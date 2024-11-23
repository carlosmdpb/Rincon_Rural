from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

# Register your models here.
class UsuarioAdmin(UserAdmin):
    # Campos que se mostrarán en la lista de usuarios
    list_display = ('username', 'email', 'dni', 'rol', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'rol')
    
    # Campos que se mostrarán al editar/crear un usuario
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'dni')}),  # Incluye el campo DNI
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
        ('Rol Personalizado', {'fields': ('rol',)}),  # Agregar campos personalizados aquí
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
