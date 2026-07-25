import os
import sys
import time
import re
import tempfile
from pathlib import Path

root_path = Path(__file__).resolve().parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
from src.core.agent import build_agent, FallbackAgentWrapper

MIN_QUERY_INTERVAL = 3

PRESETS = [
    "Tengo un error OCT en mi variador iG5A de 5.5kW al acelerar",
    "¿Qué variador me recomiendan para reemplazar un iG5A de 2.2kW?",
    "Mi variador S100 muestra error OVT, ¿qué hago?",
    "¿Cuáles son las diferencias entre iG5A y H100?",
]


@st.cache_resource
def get_cached_agent():
    return build_agent()


def parsear_etapas(respuesta: str) -> dict:
    etapas = {"diagnostico": "", "variante": "", "cita": ""}
    patrones = [
        (r"(?i)etapa\s*1[^:]*:\s*(.*?)(?=etapa\s*2|recomendación|⚙️|$)", "diagnostico"),
        (r"(?i)etapa\s*2[^:]*:\s*(.*?)(?=etapa\s*3|cita|📑|$)", "variante"),
        (r"(?i)(📑.*$)", "cita"),
    ]
    for patron, clave in patrones:
        match = re.search(patron, respuesta, re.DOTALL)
        if match:
            etapas[clave] = match.group(1).strip()
    if not etapas["cita"]:
        match_cita = re.search(r"📑.*", respuesta, re.DOTALL)
        if match_cita:
            etapas["cita"] = match_cita.group(0).strip()
    if not any(etapas.values()):
        partes = respuesta.split("\n\n")
        if len(partes) >= 3:
            etapas["diagnostico"] = partes[0]
            etapas["variante"] = partes[1]
            etapas["cita"] = "\n\n".join(partes[2:])
        elif len(partes) == 2:
            etapas["diagnostico"] = partes[0]
            etapas["cita"] = partes[1]
        else:
            etapas["diagnostico"] = respuesta
    return etapas


def extraer_preview_archivo(uploaded_file, lineas=10) -> str:
    try:
        uploaded_file.seek(0)
        if uploaded_file.name.endswith(".pdf"):
            from pypdf import PdfReader
            import io
            contenido = uploaded_file.read()
            reader = PdfReader(io.BytesIO(contenido))
            texto = ""
            for page in reader.pages[:2]:
                texto += page.extract_text() or ""
            uploaded_file.seek(0)
            lineas_texto = texto.strip().split("\n")[:lineas]
            return "\n".join(lineas_texto)
        else:
            contenido = uploaded_file.read().decode("utf-8", errors="replace")
            uploaded_file.seek(0)
            return "\n".join(contenido.split("\n")[:lineas])
    except Exception as e:
        uploaded_file.seek(0)
        return f"(No se pudo extraer preview: {e})"


def guardar_archivo(uploaded_file, destino: Path) -> Path:
    uploaded_file.seek(0)
    filepath = destino / uploaded_file.name
    filepath.write_bytes(uploaded_file.read())
    uploaded_file.seek(0)
    return filepath


def main():
    st.set_page_config(
        page_title="LS Electric AI",
        page_icon="⚡",
        layout="wide",
    )

    from config.settings import get_settings
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
            from src.rag.indexer import listar_documentos, hay_documentos
            docs = listar_documentos()
            if docs:
                st.success(f"**{len(docs)} documentos** cargados")
                with st.expander("Ver documentos"):
                    for doc in docs:
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
                    preview = extraer_preview_archivo(uf)
                    st.code(preview, language=None)

            if st.button("📤 Subir y Indexar", use_container_width=True):
                with st.spinner("Guardando y indexando..."):
                    for uf in uploaded_files:
                        guardar_archivo(uf, data_raw_dir)
                    try:
                        from src.rag.indexer import invalidar_indice
                        invalidar_indice()
                        st.cache_resource.clear()
                    except Exception as e:
                        st.error(f"Error al indexar: {e}")
                st.toast(f"✅ {len(uploaded_files)} documento(s) indexado(s)", icon="📄")
                st.rerun()

        if st.button("🗑️ Limpiar Documentos", use_container_width=True):
            with st.spinner("Limpiando..."):
                for f in data_raw_dir.iterdir():
                    if f.is_file() and f.suffix.lower() in (".pdf", ".txt", ".md"):
                        f.unlink()
                try:
                    from src.rag.indexer import invalidar_indice
                    invalidar_indice()
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
        from src.rag.indexer import hay_documentos
        if hay_documentos():
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

                etapas = parsear_etapas(response_text)

                if etapas["diagnostico"]:
                    with st.expander("🛠️ Etapa 1: Diagnóstico Técnico", expanded=True):
                        st.markdown(etapas["diagnostico"])

                if etapas["variante"]:
                    with st.expander("⚙️ Etapa 2: Recomendación", expanded=True):
                        st.markdown(etapas["variante"])

                if etapas["cita"]:
                    with st.expander("📑 Etapa 3: Fuente / Cita", expanded=True):
                        st.markdown(etapas["cita"])

                if not any(etapas.values()):
                    st.markdown(response_text)

                st.session_state.messages.append({"role": "assistant", "content": response_text})


if __name__ == "__main__":
    main()
