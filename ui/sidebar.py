import time
from pathlib import Path

import streamlit as st

from config.settings import (
    get_settings,
    SUPPORTED_EXTENSIONS,
    PRESETS,
    MIN_QUERY_INTERVAL,
)
from src.rag.indexer import list_documents, invalidate_index
from utils.file_helpers import extract_file_preview, save_file


def _render_document_status() -> None:
    """Renderiza el resumen de los documentos indexados en el RAG."""
    st.markdown("### 📊 Estado de la Base de Datos")
    try:
        documents = list_documents()
        if documents:
            st.success(f"**{len(documents)} manual(es)** activo(s)")
            with st.expander("📚 Ver índice de manuales"):
                for doc in documents:
                    st.markdown(f"• **{doc['nombre']}** (`{doc['tamaño']}`)")
        else:
            st.info("Sin manuales locales cargados")
            st.caption("Operando en modo autónomo con conocimiento preentrenado.")
    except Exception:
        st.info("Sin documentos cargados")


def _render_file_uploader(data_raw_dir: Path) -> None:
    """Renderiza la sección para cargar e indexar nuevos manuales PDF."""
    st.markdown("### 📤 Cargar Manuales")
    uploaded_files = st.file_uploader(
        "Arrastra manuales PDF o de texto",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        for uf in uploaded_files:
            with st.expander(f"📄 {uf.name} — Preview", expanded=False):
                preview = extract_file_preview(uf)
                st.code(preview, language=None)

        if st.button("📤 Procesar e Indexar", use_container_width=True):
            with st.spinner("Indexando vectores con Gemini Embedding..."):
                for uf in uploaded_files:
                    save_file(uf, data_raw_dir)
                try:
                    invalidate_index()
                    st.cache_resource.clear()
                except Exception as e:
                    st.error(f"Error al indexar: {e}")
            st.toast(f"✅ {len(uploaded_files)} manual(es) indexados", icon="📄")
            st.rerun()

    if st.button("🗑️ Vaciar Manuales RAG", use_container_width=True):
        with st.spinner("Eliminando manuales de la base local..."):
            for f in data_raw_dir.iterdir():
                if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
                    f.unlink()
            try:
                invalidate_index()
                st.cache_resource.clear()
            except Exception:
                pass
        st.toast("🗑️ Base de datos vaciada. Retornando a modo autónomo.", icon="🗑️")
        st.rerun()


def _render_presets() -> None:
    """Renderiza la sección de consultas rápidas predefinidas."""
    st.markdown("### 💡 Consultas Rápidas")
    for preset in PRESETS:
        if st.button(preset, key=f"preset_{preset[:30]}", use_container_width=True):
            st.session_state["preset_query"] = preset
            st.rerun()


def render_sidebar() -> None:
    """Renderiza el panel lateral completo de la aplicación."""
    settings = get_settings()
    data_raw_dir = settings["data_raw_dir"]

    with st.sidebar:
        st.title("⚡ LS Electric AI")
        st.caption("AgentSprint Hackathon 2026 · ReshapeX")
        st.markdown("---")

        _render_document_status()
        st.markdown("---")

        _render_file_uploader(data_raw_dir)
        st.markdown("---")

        _render_presets()
        st.markdown("---")

        if "last_query_ts" in st.session_state:
            elapsed = time.time() - st.session_state.last_query_ts
            if elapsed < MIN_QUERY_INTERVAL:
                remaining = MIN_QUERY_INTERVAL - elapsed
                st.warning(f"Límite de velocidad: espera {remaining:.1f}s")
