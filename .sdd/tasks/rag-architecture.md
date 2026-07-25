# Tareas de Trabajo: Arquitectura RAG Modular para LS Electric

## Checklist de Implementación
- [ ] **[T-201]** Crear estructura de directorios y dependencias (`config/`, `data/raw/`, `data/storage/`, `src/core/`, `src/rag/`, `src/tools/`, `requirements.txt`, `.env`).
- [ ] **[T-202]** Implementar `config/settings.py` con `get_settings()` decorado con `@lru_cache(maxsize=1)` y `pathlib`.
- [ ] **[T-203]** Crear `data/raw/manual_ls_electric.txt` con información oficial de variadores y manuales de LS Electric.
- [ ] **[T-204]** Implementar `src/rag/indexer.py` con `load_or_create_index()`.
- [ ] **[T-205]** Implementar `src/tools/rag_tools.py` con `get_lls_knowledge_tool()`.
- [ ] **[T-206]** Implementar `src/core/agent.py` con `build_agent()` retornando `ReActAgent`.
- [ ] **[T-207]** Implementar `app.py` con Streamlit, `@st.cache_resource`, historial de chat y bloque `if __name__ == "__main__":`.
- [ ] **[T-208]** Verificar sintaxis y ejecución de la aplicación.
