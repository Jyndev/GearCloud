# ⚙️ GearCloud

**GearCloud** es un sistema de gestión integral para talleres de motocicletas, desarrollado como proyecto académico para el **SENA (Servicio Nacional de Aprendizaje) - Colombia**, dentro del programa **Tecnólogo en Análisis y Desarrollo de Software (ADSO)**. El sistema está diseñado para optimizar el flujo de trabajo desde la recepción del vehículo hasta la facturación final, enfocado en una experiencia de usuario (UX) premium, minimalista y eficiente.

## 🚀 Características Principales

- **Gestión de Clientes**: Registro detallado de propietarios con normalización automática de documentos (CC/NIT) e integración con WhatsApp para comunicación directa.
- **Módulo de Motocicletas**: Control de vehículos por placa, vinculados a sus respectivos propietarios con historiales técnicos.
- **Panel de Control (Dashboard)**: Visualización en tiempo real de estadísticas clave y estado general del taller.
- **Arquitectura de Seguridad**: Sistema basado en roles (`ADMIN`, `RECEPCIÓN`, `MECÁNICO`) para proteger los datos sensibles.
- **Interfaz UI Premium**: Diseño moderno basado en Bootstrap 5.3 con estética personalizada, glassmorphism y micro-animaciones.

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.14 + [Django 6.0.4](https://www.djangoproject.com/)
- **Frontend**: HTML5, Vanilla JS, Bootstrap 5.3
- **Base de Datos**: SQLite (Desarrollo) / PostgreSQL (Producción ready)
- **Estilos**: Vanilla CSS con arquitectura de variables personalizadas.

## 📂 Estructura del Proyecto

- `config/`: Configuración central del proyecto Django.
- `users/`: Gestión de autenticación, roles y perfiles de usuario.
- `customers/`: Módulo de gestión de clientes y motocicletas.
- `dashboard/`: Vistas principales y panel de estadísticas.
- `Plantilla/`: Recursos de diseño maestro y referencias visuales.

## 🔧 Instalación

1.  **Clonar el repositorio**:
    ```bash
    git clone https://github.com/jyndev/GearCloud.git
    cd GearCloud
    ```

2.  **Crear y activar entorno virtual**:
    ```bash
    python -m venv env
    source env/bin/activate  # Linux/macOS
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install django mysqlclient python-dotenv
    ```

4.  **Aplicar migraciones**:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Crear superusuario**:
    ```bash
    python manage.py createsuperuser
    ```

6.  **Iniciar servidor**:
    ```bash
    python manage.py run_server
    ```

## 🎨 Guía de Estilo

Este proyecto sigue estrictamente la guía de diseño definida en la carpeta `Plantilla/`. Cualquier nuevo módulo debe utilizar los componentes visuales estándar:
- `.module-card`: Para contenedores de información.
- `.table-gc`: Para listado de datos.
- `.btn-gc`: Para acciones principales.
- `.btn-table-action`: Para acciones dentro de tablas.

---
**Desarrollado por [Jyn Dev] para [GearCloud — Gestión de Taller]**
© 2026 Todos los derechos reservados.
