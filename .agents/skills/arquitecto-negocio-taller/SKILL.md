---
name: arquitecto-negocio-taller
description: Actúa como un Líder Técnico y Experto en Procesos de Negocio para dictar la arquitectura de datos y la lógica funcional de un sistema de gestión de taller (GearCloud).
---

# Líder Técnico - Sistema de Gestión de Taller

Esta habilidad define la lógica de negocio profunda, el modelo de datos y los flujos de trabajo (workflows) para el sistema GearCloud, asegurando la integridad referencial y el cumplimiento de roles.

## 1. Módulo de Usuarios y Seguridad (Identidad)
- **Modelo**: `AbstractUser` personalizado con roles: `ADMIN`, `MECANICO`, `RECEPCION`.
- **Reglas de Acceso**:
    - `RECEPCION` y `ADMIN`: Crean clientes y motos.
    - `MECANICO`: Solo actualiza estados técnicos y diagnósticos.
    - `ADMIN`: Gestión total, especialmente Inventario.
- **Seguridad**: Uso de `PBKDF2`, `@login_required` y `PermissionRequiredMixin`.

## 2. Módulo de Clientes y Motos (Entidades)
- **Relación**: Cliente (1) -> Moto (N).
- **Entidades**:
    - **Cliente**: Cédula (Único), Nombre, Teléfono, Dirección.
    - **Moto**: Placa (PK/Único), Marca, Modelo, Serial Motor/Chasis.
- **Restricción**: Bloqueo de eliminación de clientes con órdenes de mantenimiento activas.

## 3. Módulo de Inventario y Ventas (Suministros)
- **Control de Stock**: Alerta visual si `stock_actual <= stock_minimo`.
- **Integración**: 
    - Ventas directas descuentan stock al instante.
    - Repuestos en mantenimiento se registran como "Salida por Servicio" vinculada a la orden.

## 4. Módulo de Mantenimiento (Workflow Core)
Máquina de estados para la Orden de Servicio:
1.  **Pendiente**: Creada por `RECEPCION`. Datos: Kilometraje, gasolina, falla y fotos.
2.  **Revisión**: Cambio automático al asignar un `MECANICO_ID`.
3.  **Reparación**: Registro de diagnóstico y adición de repuestos (descuento de stock mediante Service Layer).
4.  **Completado**: Requiere diagnóstico y resumen. Generación de reporte PDF final.

## Instrucciones de Implementación Técnica
- **SOLID**: Toda la lógica de stock DEBE ir en una **Service Layer** (`services.py`).
- **Atomicidad**: Uso de `transaction.atomic` en la creación de órdenes.
- **Referencia de Diseño Ineludible**: Antes de cualquier cambio en el frontend, es mandatorio consultar los archivos en `Plantilla/` para asegurar que cada nuevo elemento (tablas, botones, tarjetas, inputs) coincida al 100% con los componentes nativos de GearCloud (colores, sombras, radios de borde y espaciado).
- **Ubicación de Templates**: Respetar la modularidad de Django (`app_name/templates/app_name/`).
- **Optimización**: Siempre usar `.select_related('cliente', 'moto')` o `.prefetch_related` para evitar problemas N+1.

## Activación
Se activa al diseñar modelos, servicios, vistas o flujos de trabajo específicos para el negocio del taller mecánico.
