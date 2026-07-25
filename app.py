import os
import sys
from pathlib import Path

# Asegurar la inclusión de la raíz del proyecto en sys.path
root_path = Path(__file__).resolve().parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
from src.core.agent import build_agent, FallbackAgentWrapper


@st.cache_resource
def get_cached_agent():
    """Inicializa y almacena en caché el Agente para evitar reiniciar el estado en cada interacción."""
    return build_agent()


def main():
    # Configuración de página de Streamlit
    st.set_page_config(
        page_title="LLS Electric AI",
        page_icon="⚡",
        layout="wide",
    )

    # Sidebar limpia sin inputs manuales de API Key
    with st.sidebar:
        st.title("⚡ LS Electric AI")
        st.markdown("---")
        st.caption("AgentSprint Hackathon 2026 · Powered by ReshapeX")

    st.title("⚡ LLS Electric AI — Respuestas Independientes del Modelo")
    st.caption("Asistente IA de Automatización Industrial LS Electric")

    # Inicializar el agente en caché con tolerancia a fallos
    try:
        agent = get_cached_agent()
    except Exception as e:
        agent = FallbackAgentWrapper()

    # Inicialización del historial de chat en session_state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "¡Hola! Soy el asistente técnico de **LS Electric**. Escribe cualquier consulta o duda sobre equipos de automatización.",
            }
        ]

    # Renderizar el historial de chat existente
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de consulta por parte del usuario
    if prompt := st.chat_input("Escribe tu consulta o parámetro técnico..."):
        # Agregar mensaje del usuario al estado y a la UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Enviar la consulta al agente y renderizar respuesta
        with st.chat_message("assistant"):
            with st.spinner("Consultando modelo de IA..."):
                try:
                    response_text = agent.chat(prompt)
                except Exception as e:
                    fallback_agent = FallbackAgentWrapper()
                    response_text = fallback_agent.chat(prompt)

                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})


if __name__ == "__main__":
    main()
