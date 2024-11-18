from django.contrib import admin
from django.urls import path, include
from espacios import views

urlpatterns = [
    path('espacios/', views.listar_espacios, name='listar_espacios'),
    path('espacios/<int:espacio_id>/', views.detalle_espacio, name='detalle_espacio'),
    path('espacios/crear/', views.crear_espacio, name='crear_espacio'),
]