# Rincón Rural

Aplicación web para gestionar y reservar espacios de una localidad rural: por ejemplo, salas o instalaciones compartidas. Los ciudadanos consultan los espacios asociados a su código postal y solicitan reservas; los responsables gestionan espacios, eventos y autorizaciones.

![Python](https://img.shields.io/badge/Python-Backend-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-Web-092E20?logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-Frontend-E34F26?logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-Interfaz-F7DF1E?logo=javascript&logoColor=white)

Proyecto académico desarrollado en equipo con Django. Organiza la gestión municipal alrededor de usuarios, espacios y franjas horarias.

## Funcionalidades

- Registro de ciudadanos con aprobación de la cuenta antes del acceso.
- Inicio de sesión y perfil con información de espacios, reservas y eventos.
- Consulta de espacios por código postal, con capacidad, descripción, imágenes y horarios.
- Reservas con comprobaciones de fechas, horario de apertura y solapamientos.
- Reservas agrupadas y dependencias entre espacios.
- Gestión y cancelación de reservas, incluidas las que coinciden con un evento.
- Autorización de reservas y notificaciones por correo.
- Gestión mediante Django Admin y valoración general de la aplicación.

## Tecnologías y arquitectura

| Área | Implementación |
| --- | --- |
| Backend | Python y Django |
| Interfaz | Plantillas HTML, CSS y JavaScript |
| Datos | SQLite en la configuración incluida |
| Usuarios | Modelo propio basado en `AbstractUser` |
| Administración | Django Admin |
| Imágenes | `ImageField`, que requiere Pillow |
| Correo | Llamadas SMTP desde los modelos |

El proyecto separa sus funciones en aplicaciones Django: `usuarios`, `espacios`, `reservas`, `eventos` y `calificaciones`. Las vistas y formularios gestionan las interacciones; los modelos representan las entidades y algunas acciones asociadas a sus cambios.

## Ejecutar en local

Requisitos: Python, Django 4.2 o posterior y Pillow para el manejo de imágenes.

```sh
git clone https://github.com/carlosmdpb/Rincon_Rural.git
cd Rincon_Rural
python -m venv .venv
```

Activar el entorno:

```powershell
# Windows / PowerShell
.\.venv\Scripts\Activate.ps1
```

```sh
# Linux / macOS
source .venv/bin/activate
```

```sh
python -m pip install -r requirements.txt
python -m pip install Pillow
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Inicio: [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
- Registro: [http://127.0.0.1:8000/usuarios/registro/](http://127.0.0.1:8000/usuarios/registro/).
- Administración: [http://127.0.0.1:8000/usuarios/admin/](http://127.0.0.1:8000/usuarios/admin/).

### Uso de la aplicación

1. Crear espacios y usuarios de demostración con el mismo código postal.
2. Consultar la lista de espacios y solicitar una reserva dentro de su horario.
3. Revisar la reserva desde el perfil y la administración.

Las nuevas cuentas pasan por aprobación del administrador. El sistema envía notificaciones por correo al activar cuentas y autorizar reservas.

## Estructura

```text
app_rural/      Configuración y rutas del proyecto
usuarios/       Cuentas, roles y perfil
espacios/       Instalaciones, imágenes y dependencias
reservas/       Fechas, disponibilidad y reservas agrupadas
eventos/        Actividades y conflictos con reservas
calificaciones/ Valoración de la aplicación
static/         Recursos de la interfaz
manage.py       Comandos Django
```

Para leer las reglas del sistema: [modelo de espacios](espacios/models.py), [validación de reservas](reservas/forms.py) y [rutas](app_rural/urls.py).
