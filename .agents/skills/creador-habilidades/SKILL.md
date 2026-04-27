---
name: creador-habilidades
description: Utiliza esta habilidad para crear nuevas habilidades personalizadas en este espacio de trabajo, asegurando que sigan el formato correcto y estén en español.
---

# Creador de Habilidades

Esta habilidad permite al asistente crear nuevas habilidades (skills) dentro del espacio de trabajo siguiendo las convenciones oficiales de Antigravity.

## Cuándo usar esta habilidad
Activa esta habilidad cuando el usuario solicite crear, modificar o extender las capacidades del asistente mediante una nueva "habilidad" persistente.

## Instrucciones para el Asistente

Para crear una nueva habilidad, debes seguir estrictamente estos pasos:

### 1. Definición y Estructura
- **Ubicación**: Todas las habilidades deben residir en `.agents/skills/<nombre-habilidad>/`.
- **Archivo Obligatorio**: Cada habilidad DEBE tener un archivo `SKILL.md`.
- **Idioma**: Tanto el nombre de la habilidad como sus instrucciones internas deben estar en **español**, a menos que se solicite lo contrario.

### 2. Formato del archivo SKILL.md
El archivo debe comenzar con un bloque de metadatos YAML (frontmatter) y seguir con el contenido en Markdown:

```markdown
---
name: nombre-de-la-habilidad
description: Descripción detallada en tercera persona de lo que hace esta habilidad.
---

# Título de la Habilidad

[Instrucciones detalladas aquí...]
```

### 3. Componentes Adicionales (Opcional)
Si la habilidad es compleja, puedes organizar archivos adicionales en las siguientes subcarpetas:
- `scripts/`: Scripts ejecutables que la habilidad utiliza.
- `examples/`: Ejemplos de referencia para el usuario o el asistente.
- `resources/`: Plantillas, archivos de configuración o documentos de apoyo.

### 4. Registro y Verificación
Una vez creada la habilidad, confirma al usuario su ubicación y explícale brevemente cómo puede invocarla o en qué situaciones se activará automáticamente por "descubrimiento progresivo" (basado en la descripción de los metadatos).

## Ejemplo de Instrucciones Internas
Al escribir las instrucciones de la nueva habilidad, asegúrate de ser específico sobre los "prompts" o reglas que el asistente debe seguir cuando la habilidad esté activa.
