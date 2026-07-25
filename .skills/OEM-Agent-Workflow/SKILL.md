---
name: OEM-Agent-Workflow
description: >
  Orquesta la regla de negocio constante para Agentes de IA industriales y OEMs (ej. LS Electric):
  1. Consultar Guía/Manual Técnico (Diagnóstico de errores y fallas).
  2. Verificar Variantes y Sustitutos (Migración de modelos antiguos a nuevos).
  3. Generar Respuesta Limpia Grounded con Cita Oficial del Manual.
mode: skill
priority: high
---

# OEM Agent Workflow (Regla de Negocio Constante)

Esta habilidad define y orquesta el flujo de trabajo estándar en 3 etapas obligatorias para cualquier Agente de IA enfocado en fabricantes de automatización industrial (OEMs como LS Electric, WEG, Siemens, etc.).

## 🔄 Las 3 Etapas del Flujo de Trabajo

### Etapa 1: Consulta de Guía / Manual Técnico 🔍
- **Propósito**: Extraer el diagnóstico preciso del código de falla, causa raíz y acciones correctivas.
- **Acción**: Consultar la base de conocimiento (RAG / DB de manuales de usuario).
- **Entregable**: Objeto con `codigo`, `nombre_falla`, `causa_probable`, `pasos_solucion`, `manual_origen`, `seccion` y `pagina`.

### Etapa 2: Verificación de Variantes y Reemplazos ⚙️
- **Propósito**: Evaluar la matriz de productos para ofrecer la sustitución o migración de equipos descontinuados o alternativos.
- **Acción**: Buscar en el catálogo de productos por potencia, voltaje y familia.
- **Entregable**: Objeto con `modelo_anterior`, `reemplazo_directo`, `ventajas_migracion` y `compatibilidad_dimensiones`.

### Etapa 3: Generación de Respuesta Limpia Grounded con Cita 📑
- **Propósito**: Sintetizar la respuesta final para el usuario de forma clara, profesional y 100% fundamentada (sin alucinaciones).
- **Regla Estricta de Formato**:
  1. **Sección 1 (Diagnóstico Técnico)**: `🛠️ Diagnóstico Técnico`
  2. **Sección 2 (Recomendación de Variante)**: `⚙️ Recomendación de Variante y Reemplazo`
  3. **Sección 3 (Cita de Origen)**: `📑 Cita Oficial del Manual` (Indicar Manual, Sección y Página exacta).
