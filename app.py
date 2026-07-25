import os
import sys
import time
import re
import io
from pathlib import Path
from typing import List, Dict

import streamlit as st
from pypdf import PdfReader

from config.settings import get_settings, SUPPORTED_EXTENSIONS
from src.core.agent import FallbackAgentWrapper
from src.core.agent_factory import AgentFactory
from src.rag.indexer import (
    list_documents,
    has_documents,
    invalidate_index,
)

MIN_QUERY_INTERVAL = 3

PRESETS = [
    "Tengo un error OCT en mi variador iG5A de 5.5kW al acelerar",
    "¿Qué variador me recomiendan para reemplazar un iG5A de 2.2kW?",
    "Mi variador S100 muestra error OVT, ¿qué hago?",
    "¿Cuáles son las diferencias entre iG5A y H100?",
]


@st.cache_resource
def get_cached_agent():
    """Construye y cachea el agente RAG."""
    return AgentFactory.build_agent()


def parse_stages(response: str) -> Dict[str, str]:
    """Parsea la respuesta del agente en las 3 etapas.

    Args:
        response: Respuesta completa del agente.

    Returns:
        Diccionario con las 3 etapas parseadas.
    """
    stages = {"diagnostico": "", "variante": "", "cita": ""}
    patterns = [
        (r"(?i)etapa\s*1[^:]*:\s*(.*?)(?=etapa\s*2|recomendación|⚙️|$)", "diagnostico"),
        (r"(?i)etapa\s*2[^:]*:\s*(.*?)(?=etapa\s*3|cita|📑|$)", "variante"),
        (r"(?i)(📑.*$)", "cita"),
    ]
    for pattern, key in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            stages[key] = match.group(1).strip()
    if not stages["cita"]:
        match_cita = re.search(r"📑.*", response, re.DOTALL)
        if match_cita:
            stages["cita"] = match_cita.group(0).strip()
    if not any(stages.values()):
        parts = response.split("\n\n")
        if len(parts) >= 3:
            stages["diagnostico"] = parts[0]
            stages["variante"] = parts[1]
            stages["cita"] = "\n\n".join(parts[2:])
        elif len(parts) == 2:
            stages["diagnostico"] = parts[0]
            stages["cita"] = parts[1]
        else:
            stages["diagnostico"] = response
    return stages


def extract_file_preview(uploaded_file, lines: int = 10) -> str:
    """Extrae preview de un archivo subido.

    Args:
        uploaded_file: Archivo de Streamlit.
        lines: Número de líneas a extraer.

    Returns:
        Preview del archivo como string.
    """
    try:
        uploaded_file.seek(0)
        if uploaded_file.name.endswith(".pdf"):
            contenido = uploaded_file.read()
            reader = PdfReader(io.BytesIO(contenido))
            text = ""
            for page in reader.pages[:2]:
                text += page.extract_text() or ""
            uploaded_file.seek(0)
            preview_lines = text.strip().split("\n")[:lines]
            return "\n".join(preview_lines)
        else:
            contenido = uploaded_file.read().decode("utf-8", errors="replace")
            uploaded_file.seek(0)
            return "\n".join(contenido.split("\n")[:lines])
    except Exception as e:
        uploaded_file.seek(0)
        return f"(No se pudo extraer preview: {e})"


def save_file(uploaded_file, destination: Path) -> Path:
    """Guarda un archivo subido en el destino especificado.

    Args:
        uploaded_file: Archivo de Streamlit.
        destination: Directorio destino.

    Returns:
        Ruta del archivo guardado.
    """
    uploaded_file.seek(0)
    filepath = destination / uploaded_file.name
    filepath.write_bytes(uploaded_file.read())
    uploaded_file.seek(0)
    return filepath


def main():
    """Función principal de la aplicación Streamlit."""
    st.set_page_config(
        page_title="LS Electric AI",
        page_icon="⚡",
        layout="wide",
    )

    settings = get_settings()
    data_raw_dir = settings["data_raw_dir"]
    storage_dir = settings["storage_dir"]
    data_raw_dir.mkdir(parents=True, exist_ok=True)

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

    st.title("⚡ LS Electric AI — Diagnóstico Industrial")
    try:
        if has_documents():
            st.caption("Modo RAG: respuestas fundamentadas en documentos cargados")
        else:
            st.caption("Modo autónomo: respuestas con conocimiento general de Gemini")
    except Exception:
        st.caption("Asistente IA de Automatización Industrial LS Electric")

    try:
        agent = get_cached_agent()
    except Exception:
        agent = FallbackAgentWrapper()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "¡Hola! Soy el asistente técnico de **LS Electric**. Puedo ayudarte con:\n\n"
                "- **Diagnóstico de fallas** en variadores, PLCs, HMIs\n"
                "- **Recomendación de equipos** y reemplazos\n"
                "- **Citas técnicas** de manuales oficiales\n\n"
                "Escribe tu consulta, usa los botones de la barra lateral, o sube documentos PDF para enriquecer mis respuestas.",
            }
        ]

    if "last_query_ts" not in st.session_state:
        st.session_state.last_query_ts = 0

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    preset_query = st.session_state.pop("preset_query", None)
    prompt = preset_query or st.chat_input("Escribe tu consulta técnica...")

    if prompt:
        elapsed = time.time() - st.session_state.last_query_ts
        if elapsed < MIN_QUERY_INTERVAL and not preset_query:
            st.toast(f"Rate limit: espera {MIN_QUERY_INTERVAL - elapsed:.1f}s", icon="⏱️")
            return

        st.session_state.last_query_ts = time.time()
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Procesando en 3 etapas..."):
                try:
                    response_text = agent.chat(prompt)
                except Exception:
                    fallback_agent = FallbackAgentWrapper()
                    response_text = fallback_agent.chat(prompt)

                stages = parse_stages(response_text)

                if stages["diagnostico"]:
                    with st.expander("🛠️ Etapa 1: Diagnóstico Técnico", expanded=True):
                        st.markdown(stages["diagnostico"])

                if stages["variante"]:
                    with st.expander("⚙️ Etapa 2: Recomendación", expanded=True):
                        st.markdown(stages["variante"])

                if stages["cita"]:
                    with st.expander("📑 Etapa 3: Fuente / Cita", expanded=True):
                        st.markdown(stages["cita"])

                if not any(stages.values()):
                    st.markdown(response_text)

                st.session_state.messages.append({"role": "assistant", "content": response_text})


if __name__ == "__main__":
    main()
