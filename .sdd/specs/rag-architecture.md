# Spec: Arquitectura RAG Modular para LS Electric (LLS Electric AI)

## Contexto y Motivación
Refactorización del repositorio `proyecto-Reshapex` para implementar una arquitectura RAG (Retrieval-Augmented Generation) limpia, modular y desacoplada utilizando LlamaIndex (versión 0.10+), OpenAI y Streamlit. Esta arquitectura permite responder a ingenieros y técnicos sobre manuales, fallas y catálogos de LS Electric sin variables globales con efectos secundarios.

## Actores y Flujos
* **Ingeniero/Técnico de Planta**: Ingresa consultas a través de la interfaz web en Streamlit.
* **Agente ReAct (LlamaIndex)**: Procesa el mensaje, evalúa si necesita consultar la base de conocimiento y ejecuta la herramienta RAG.
* **Motor RAG (Indexador)**: Carga o persiste el índice vectorial de documentos técnicos de LS Electric en disco.

## Metas (Goals)
1. Estructura modular limpia (`config/`, `data/raw/`, `data/storage/`, `src/core/`, `src/rag/`, `src/tools/`).
2. Configuración inmutable y en caché usando `@lru_cache`.
3. Indexación eficiente con `load_or_create_index()` reutilizando almacenamiento en disco.
4. Herramienta RAG encapsulada en `QueryEngineTool` con metadatos descriptivos ("base_conocimiento_lls").
5. Agente `ReActAgent` inicializado y almacenado en caché con `@st.cache_resource` para evitar reinicios por turno en Streamlit.
6. Cero uso de variables globales con efectos secundarios fuera de funciones.

## No-Metas (Non-Goals)
1. No usar frameworks pesados innecesarios ni cadenas monolíticas desordenadas.
2. No reinicializar el índice ni el agente en cada interacción del usuario.

## Criterios de Aceptación (AC)
- [ ] **AC-1**: Carga de configuración mediante `get_settings()` usando `pathlib` y `@lru_cache`.
- [ ] **AC-2**: Verificación de `STORAGE_DIR`: si está vacío crea e indexa documentos de `data/raw/` y persiste; si existe, carga de disco.
- [ ] **AC-3**: Herramienta RAG `get_lls_knowledge_tool()` retorna `QueryEngineTool` con `similarity_top_k=3`.
- [ ] **AC-4**: `build_agent()` retorna `ReActAgent` con `gpt-4o-mini` y `text-embedding-3-small`.
- [ ] **AC-5**: `app.py` utiliza `@st.cache_resource` para inicializar el agente y mantiene el historial de chat en `st.session_state`.
