# Tareas de Trabajo: Mejoras UI/UX y Refactorización Frontend — LS Electric AI

## Checklist de Implementación

- [ ] **[T-201]** Crear módulo `ui/theme.py` con el sistema de diseño CSS y Badges de Estado.
  - **Criterio de Done**: `ui/theme.py` define `apply_custom_theme()` e inyecta estilos oscuros modernos (`#FFD700` primary, bordes redondeados, sombras en cards).
  - **Commit Sugerido**: `feat(ui): create theme.py for custom CSS design system`

- [ ] **[T-202]** Refactorizar `ui/chat.py` descomponiendo el componente en funciones SRP.
  - **Criterio de Done**: `chat.py` está separado en `_render_header()`, `_render_history()`, `_render_stage_cards()` y agrega el control para limpiar chat.
  - **Commit Sugerido**: `refactor(ui): apply SRP to chat.py and add chat reset feature`

- [ ] **[T-203]** Refactorizar `ui/sidebar.py` mejorando la disposición visual de PDFs y Presets.
  - **Criterio de Done**: La barra lateral muestra el estado RAG con badges estilizados y presets organizados limpiamente.
  - **Commit Sugerido**: `refactor(ui): enhance sidebar document status and presets layout`

- [ ] **[T-204]** Integrar el tema global en `app.py` y realizar prueba de navegación completa.
  - **Criterio de Done**: La aplicación compila y renderiza con el tema visual activo, respondiendo correctamente en 3 etapas.
  - **Commit Sugerido**: `feat(ui): connect custom theme in app.py`

- [ ] **[T-205]** Ejecución de verificación visual y funcional en `.sdd/specs/verify.md`.
  - **Criterio de Done**: Todos los criterios de aceptación (AC-1 a AC-5) están marcados y verificados.
  - **Commit Sugerido**: `docs(sdd): update verify results for UI/UX enhancements`
