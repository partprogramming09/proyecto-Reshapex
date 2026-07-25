import time
from typing import Dict, Any

import streamlit as st

from config.settings import MIN_QUERY_INTERVAL
from src.core.agent import FallbackAgentWrapper
from src.rag.indexer import has_documents, list_documents
from utils.response_parser import parse_stages
from ui.theme import render_status_badge


def _init_session_state() -> None:
    """Inicializa variables de estado de sesión si no existen."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "¡Hola! Soy el asistente técnico oficial de **LS Electric** (OEM).\n\n"
                "Puedo ayudarte con:\n"
                "- **Diagnóstico de fallas** en variadores (`OCT`, `OVT`, `ETH`, `NTC`), PLCs y HMIs.\n"
                "- **Matriz de migración y recomendación** (ej. reemplazar `iG5A` por `S100`/`H100`).\n"
                "- **Citas y fuentes oficializadas** de manuales técnicos en 3 etapas.",
            }
        ]
    if "last_query_ts" not in st.session_state:
        st.session_state.last_query_ts = 0


def _render_header(agent: Any) -> None:
    """Renderiza la cabecera principal del chat con título, badge de estado y botón de reset."""
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.title("⚡ LS Electric AI — Diagnóstico Industrial")
        try:
            documents = list_documents()
            render_status_badge(is_rag=has_documents(), doc_count=len(documents))
        except Exception:
            render_status_badge(is_rag=False)

    with col2:
        st.write("")
        if st.button("🗑️ Limpiar Chat", use_container_width=True, help="Reiniciar historial de la conversación"):
            _reset_chat_session(agent)
            st.rerun()

    st.markdown("---")


def _reset_chat_session(agent: Any) -> None:
    """Limpia el historial del chat en la interfaz y en el buffer del agente."""
    st.session_state.messages = []
    if hasattr(agent, "memory_manager"):
        agent.memory_manager.clear()
    elif hasattr(agent, "chat_history"):
        agent.chat_history.clear()
    _init_session_state()


def _render_stage_cards(stages: Dict[str, str], raw_response: str) -> None:
    """Renderiza las 3 etapas del diagnóstico técnico en tarjetas/expanders estilizados."""
    if stages.get("diagnostico"):
        with st.expander("🛠️ Etapa 1: Diagnóstico Técnico", expanded=True):
            st.markdown(stages["diagnostico"])

    if stages.get("variante"):
        with st.expander("⚙️ Etapa 2: Recomendación de Equipos y Variantes", expanded=True):
            st.markdown(stages["variante"])

    if stages.get("cita"):
        with st.expander("📑 Etapa 3: Cita de Origen / Fuente", expanded=True):
            st.markdown(stages["cita"])

    if not any(stages.values()):
        st.markdown(raw_response)


def render_chat(agent: Any) -> None:
    """Renderiza el área principal del chat aplicando Clean Code y SRP.

    Args:
        agent: Instancia del agente (ReActAgentWrapper o FallbackAgentWrapper).
    """
    _init_session_state()
    _render_header(agent)

    # Renderizado del historial de mensajes
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "⚡"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Entrada de consulta
    preset_query = st.session_state.pop("preset_query", None)
    prompt = preset_query or st.chat_input("Escribe tu consulta técnica sobre variadores o PLCs LS Electric...")

    if prompt:
        elapsed = time.time() - st.session_state.last_query_ts
        if elapsed < MIN_QUERY_INTERVAL and not preset_query:
            st.toast(f"Frecuencia máxima: espera {MIN_QUERY_INTERVAL - elapsed:.1f}s", icon="⏱️")
            return

        st.session_state.last_query_ts = time.time()
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚡"):
            with st.spinner("Ejecutando diagnóstico en 3 etapas..."):
                try:
                    response_text = agent.chat(prompt)
                except Exception as e:
                    print(f"[Info] Error en agente principal, invocando fallback: {e}")
                    fallback_agent = FallbackAgentWrapper()
                    response_text = fallback_agent.chat(prompt)

                stages = parse_stages(response_text)
                _render_stage_cards(stages, response_text)

                st.session_state.messages.append({"role": "assistant", "content": response_text})
