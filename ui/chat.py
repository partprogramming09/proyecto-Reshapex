import time

import streamlit as st

from config.settings import MIN_QUERY_INTERVAL
from src.core.agent import FallbackAgentWrapper
from src.rag.indexer import has_documents
from utils.response_parser import parse_stages


def render_chat(agent):
    """Renderiza el area principal del chat: titulo, historial, input y respuesta.

    Args:
        agent: Instancia del agente (ReActAgent o FallbackAgentWrapper).
    """
    st.title("⚡ LS Electric AI — Diagnóstico Industrial")
    try:
        if has_documents():
            st.caption("Modo RAG: respuestas fundamentadas en documentos cargados")
        else:
            st.caption("Modo autónomo: respuestas con conocimiento general de Gemini")
    except Exception:
        st.caption("Asistente IA de Automatización Industrial LS Electric")

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
