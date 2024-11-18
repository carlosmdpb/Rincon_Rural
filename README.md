# Gestión de Espacios Rurales

## Descripción

**Sistema de Gestión Rural** es una aplicación web desarrollada en **Django** (Python) que facilita la administración y reserva de espacios rurales en pueblos con menos de 15,000 habitantes. La plataforma cuenta con dos interfaces principales:

1. **Interfaz de Usuario**: Para usuarios que buscan reservar espacios rurales.
2. **Interfaz de Administrador**: Para administradores que gestionan los espacios disponibles en su localidad.

Esta aplicación promueve el desarrollo rural al facilitar el acceso a recursos y fomentar el turismo sostenible en áreas de baja densidad poblacional.

---

## Funcionalidades

### Para Usuarios
- Registro e inicio de sesión.
- Búsqueda de espacios rurales por pueblo y disponibilidad.
- Visualización de detalles de los espacios (descripción, fotos, capacidad, precios, etc.).
- Reserva de espacios disponibles.
- Gestión de reservas (visualización, modificación o cancelación).

### Para Administradores
- Registro e inicio de sesión.
- Creación de espacios rurales en su pueblo (nombre, descripción, fotos, capacidad, disponibilidad, etc.).
- Eliminación de espacios que ya no estén disponibles.
- Visualización de las reservas realizadas en los espacios administrados.

---

## Tecnologías Utilizadas

- **Backend**: Django (Python)
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: HTML5, CSS3, JavaScript (utilizando frameworks como Bootstrap para el diseño responsivo).
- **Otros**: Django Admin para la gestión del panel de administradores.

---

## Requisitos del Sistema

1. **Python**: Versión 3.8 o superior.
2. **Django**: Versión 4.x o superior.
3. **Base de datos**: SQLite para pruebas locales o PostgreSQL para producción.
4. Dependencias adicionales listadas en `requirements.txt`.

---

## Instalación y Configuración

### Clonar el repositorio
```bash
git clone https://github.com/usuario/gestion-espacios-rurales.git
cd gestion-espacios-rurales
python3.12 venv venv
source venv/bin/active
pip -r install requirements.txt
