# Spec: Mejoras de Interfaz de Usuario y Experiencia de Usuario (UI/UX) — LS Electric AI

## Contexto y Motivación
El asistente técnico de **LS Electric AI** cuenta con un motor RAG en 3 etapas funcional. Sin embargo, la interfaz actual en Streamlit requiere un salto de calidad visual y funcional (UX Premium) para:
1. Impactar visualmente con un diseño moderno, estético, oscuro e industrial (Gold & Dark Mode).
2. Facilitar la interacción del usuario reduciendo fricción (indicadores de estado RAG claros, avatars personalizados, animaciones micro-interactivas, acciones de copiado y botón para limpiar chat).
3. Aplicar principios de **Clean Code** y **Single Responsibility Principle (SRP)** en los componentes UI (`ui/chat.py`, `ui/sidebar.py`, `ui/theme.py`, `utils/`).

## Actores y Flujos
- **Ingeniero / Técnico Industrial (Usuario)**:
  - Ingresa a la app y visualiza de inmediato la insignia del sistema ("Modo RAG Activo" o "Modo Autónomo").
  - Consulta errores o modelos manualmente o mediante accesos rápidos (Presets).
  - Visualiza el diagnóstico presentado en 3 tarjetas/expanders con código de colores claro (🛠️ Diagnóstico, ⚙️ Recomendación, 📑 Fuente).
  - Puede copiar la respuesta completa o limpiar el historial de la conversación en 1 clic.
  - Sube manuales PDF en la barra lateral con preview rápido y estado de indexación en tiempo real.

## Metas (Goals)
1. **Rediseño Visual Premium (Visual Excellence)**: Implementar una paleta de colores industrial armoniosa (`#FFD700` Gold, `#0E1117` Dark Base, `#1E232A` Cards) con bordes redondeados, sombras suaves y tipografía limpia.
2. **Experiencia de Chat Mejorada (UX)**:
   - Avatars diferenciados para Usuario (👤) y Asistente (⚡ LS Electric AI).
   - Botón de acción para **Limpiar Conversación** y botón para **Copiar Diagnóstico**.
   - Badges visuales de estado RAG (Verde para RAG con N PDFs, Azul para Autónomo).
3. **Refactorización de Código (Clean Code & SRP)**:
   - Crear `ui/theme.py` para desacoplar inyección de CSS customizado y componentes de diseño.
   - Modularizar `ui/sidebar.py` y `ui/chat.py` en funciones pequeñas con responsabilidad única (<50 líneas por función).
   - Tipar completamente las respuestas y modelos auxiliares en `utils/`.

## No-Metas (Non-Goals)
1. Cambiar la lógica del motor LLM o del motor RAG de `LlamaIndex` / `Gemini`.
2. Reemplazar Streamlit por otro framework web (se mantendrá Streamlit aprovechando CSS personalizado inyectado).

## Criterios de Aceptación (AC)
- [ ] **AC-1**: Inyección de CSS global con estilos modernos (glassmorphism sutil, bordes suaves de 12px, hover en botones).
- [ ] **AC-2**: Indicador de estado RAG visual destacado en la cabecera del chat (badge con ícono y contador de documentos).
- [ ] **AC-3**: Renderizado de respuesta en 3 etapas visualmente diferenciadas mediante Cards/Expanders estilizados.
- [ ] **AC-4**: Botón de **"🗑️ Limpiar Conversación"** en la interfaz para reiniciar el `AgentMemoryManager`.
- [ ] **AC-5**: Refactorización de `ui/` separando estilos (`theme.py`), barra lateral (`sidebar.py`) y chat (`chat.py`).
