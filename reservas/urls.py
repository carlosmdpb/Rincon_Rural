# reservas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear_reserva, name='crear_reserva'),
    path('', views.listar_reservas, name='listar_reservas'),
    path('horas-disponibles/<int:espacio_id>/<str:fecha>/', views.horas_disponibles, name='horas_disponibles'),
]
