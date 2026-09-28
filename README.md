# Rincón Rural

Aplicación web para gestionar y reservar espacios de una localidad rural: por ejemplo, salas o instalaciones compartidas. Los ciudadanos consultan los espacios asociados a su código postal y solicitan reservas; los responsables gestionan espacios, eventos y autorizaciones.

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

Requisitos: Python compatible con la versión de Django instalada. `requirements.txt` declara `Django>=4.2` sin límite superior; no fija un entorno reproducible.

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

Pillow se instala aparte porque los modelos usan imágenes pero la dependencia no figura en `requirements.txt`.

- Inicio: [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
- Registro: [http://127.0.0.1:8000/usuarios/registro/](http://127.0.0.1:8000/usuarios/registro/).
- Administración: [http://127.0.0.1:8000/usuarios/admin/](http://127.0.0.1:8000/usuarios/admin/).

El repositorio incluye `db.sqlite3`. Para una demostración con datos propios, hacer una copia de seguridad y utilizar una base nueva creada por las migraciones. No se publican credenciales de usuarios existentes.

### Recorrido de prueba

1. Crear espacios y usuarios de demostración con el mismo código postal.
2. Consultar la lista de espacios y solicitar una reserva dentro de su horario.
3. Revisar la reserva desde el perfil y la administración.

Las cuentas registradas comienzan inactivas. Su activación y otras acciones pueden enviar correo: hay que configurar el correo para un entorno de pruebas antes de recorrer esos flujos.

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

## Estado y limitaciones

La configuración incluida es de desarrollo con SQLite y `DEBUG=True`. No incorpora configuración PostgreSQL de producción.

Antes de publicar o desplegar, es necesario retirar las credenciales SMTP incluidas en el código, revocarlas y sustituirlas por configuración externa. También debe revisarse la base SQLite para excluir datos personales.

Los archivos de pruebas requieren corrección: `usuarios/tests.py` realiza consultas al importar el módulo y usa símbolos no importados. No se presenta como una suite funcional. Tras corregirla, el comando Django será `python manage.py test`.
