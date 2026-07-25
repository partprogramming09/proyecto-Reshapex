import time

import streamlit as st

from config.settings import (
    get_settings,
    SUPPORTED_EXTENSIONS,
    PRESETS,
    MIN_QUERY_INTERVAL,
)
from src.rag.indexer import list_documents, has_documents, invalidate_index
from utils.file_helpers import extract_file_preview, save_file


def render_sidebar():
    """Renderiza el sidebar completo: estado RAG, upload, presets, throttle."""
    settings = get_settings()
    data_raw_dir = settings["data_raw_dir"]

    with st.sidebar:
        st.title("⚡ LS Electric AI")
        st.markdown("---")
        st.caption("AgentSprint Hackathon 2026 · Powered by ReshapeX")

        st.markdown("### 📊 Estado RAG")
        try:
            documents = list_documents()
            if documents:
                st.success(f"**{len(documents)} documentos** cargados")
                with st.expander("Ver documentos"):
                    for doc in documents:
                        st.text(f"• {doc['nombre']} ({doc['tamaño']})")
            else:
                st.info("Sin documentos cargados")
                st.caption("Modo autónomo: responde con conocimiento general")
        except Exception:
            st.info("Sin documentos cargados")

        st.markdown("---")

        st.markdown("### 📤 Subir Documentos")
        uploaded_files = st.file_uploader(
            "Arrastra PDFs o archivos de texto",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        if uploaded_files:
            for uf in uploaded_files:
                with st.expander(f"📄 {uf.name} — Preview", expanded=False):
                    preview = extract_file_preview(uf)
                    st.code(preview, language=None)

            if st.button("📤 Subir y Indexar", use_container_width=True):
                with st.spinner("Guardando y indexando..."):
                    for uf in uploaded_files:
                        save_file(uf, data_raw_dir)
                    try:
                        invalidate_index()
                        st.cache_resource.clear()
                    except Exception as e:
                        st.error(f"Error al indexar: {e}")
                st.toast(f"✅ {len(uploaded_files)} documento(s) indexado(s)", icon="📄")
                st.rerun()

        if st.button("🗑️ Limpiar Documentos", use_container_width=True):
            with st.spinner("Limpiando..."):
                for f in data_raw_dir.iterdir():
                    if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
                        f.unlink()
                try:
                    invalidate_index()
                    st.cache_resource.clear()
                except Exception:
                    pass
            st.toast("🗑️ Documentos limpiados. Modo autónomo.", icon="🗑️")
            st.rerun()

        st.markdown("---")

        st.markdown("### Consultas Rápidas")
        for preset in PRESETS:
            if st.button(preset, key=f"preset_{preset[:30]}", use_container_width=True):
                st.session_state["preset_query"] = preset
                st.rerun()

        st.markdown("---")
        if "last_query_ts" in st.session_state:
            elapsed = time.time() - st.session_state.last_query_ts
            if elapsed < MIN_QUERY_INTERVAL:
                remaining = MIN_QUERY_INTERVAL - elapsed
                st.warning(f"Espera {remaining:.1f}s")
