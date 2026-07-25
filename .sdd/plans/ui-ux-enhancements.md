# Plan Técnico: Mejoras UI/UX y Refactorización Clean Code — LS Electric AI

## Análisis Arquitectónico
Para elevar el estándar estético de la aplicación Streamlit sin alterar la lógica de negocio ni romper la compatibilidad, aplicaremos la arquitectura por capas para el frontend:

```
ui/
├── __init__.py
├── theme.py          <-- [NUEVO] Inyector de CSS global, variables HSL/HEX y Badges
├── chat.py           <-- Componente principal del área de mensajes y renderizado de 3 etapas
└── sidebar.py        <-- Componente de carga de PDFs, presets y estado de documentos
```

### Principios a Aplicar:
1. **Clean Code & SRP**:
   - `theme.py`: Única responsabilidad de definir e inyectar el sistema de diseño CSS.
   - `sidebar.py`: Maneja exclusivamente el panel lateral, uploader de PDFs y botones preset.
   - `chat.py`: Encargado único del ciclo de conversación y renderizado del historial.
2. **Visual Excellence**:
   - Primary: `#FFD700` (Oro LS Electric).
   - Card Background: `#1A1E24` con bordes `#2D333B` de `8px`.
   - Hover effects en botones y presets.
   - Micro-animaciones en tarjetas expandibles.

---

## Archivos por Modificar / Crear

1. `ui/theme.py` (Crear)
   - Contiene la función `apply_custom_theme()` con CSS customizado inyectado vía `st.markdown(..., unsafe_allow_html=True)`.
   - Define componentes visuales reusables como `render_status_badge(is_rag: bool, count: int)`.

2. `ui/chat.py` (Modificar / Refactorizar)
   - Reorganizar en sub-funciones: `_render_header()`, `_render_message_history()`, `_render_stage_cards()`, `_render_chat_controls()`.
   - Conectar botón para limpiar conversación (`agent.memory_manager.clear()` o reiniciar `st.session_state.messages`).

3. `ui/sidebar.py` (Modificar / Refactorizar)
   - Mejorar estética del uploader de archivos y botones de presets con íconos organizados en grid o columnas.
   - Añadir información visual clara del estado de los documentos cargados.

4. `app.py` (Modificar)
   - Invocar `apply_custom_theme()` al inicio del punto de entrada.

5. `utils/response_parser.py` (Mantener / Extender)
   - Asegurar que `DiagnosticReport` provea métodos formateados para la UI.

---

## Riesgos y Mitigaciones
- **Riesgo**: Que los estilos de Streamlit sobrescriban el CSS personalizado.
  - *Mitigación*: Usar selectores específicos de Streamlit (`div[data-testid="stSidebar"]`, `div.stChatMessage`, `div[data-testid="stExpander"]`) e `!important` solo cuando sea estrictamente necesario.
- **Riesgo**: Que la limpieza de memoria desincronice `st.session_state.messages` con `AgentMemoryManager`.
  - *Mitigación*: Crear una función helper unificada `reset_chat_session(agent)` que limpie ambos estados simultáneamente.
