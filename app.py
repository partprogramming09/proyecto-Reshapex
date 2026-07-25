import sys
from pathlib import Path

# Asegurar la inclusión de la raíz del proyecto en sys.path
root_path = Path(__file__).resolve().parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
from src.core.agent import build_agent


@st.cache_resource
def get_cached_agent():
    """Inicializa y almacena en caché el ReActAgent para evitar reiniciar el estado en cada interacción."""
    return build_agent()


def main():
    # Configuración de página de Streamlit
    st.set_page_config(
        page_title="LLS Electric AI",
        page_icon="⚡",
        layout="wide",
    )

    st.title("⚡ LLS Electric AI — Asistente RAG Modular")
    st.caption("Sistema de Asistencia Técnica RAG con ReActAgent y LlamaIndex para LLS Electric")

    # Inicializar el agente en caché
    try:
        agent = get_cached_agent()
    except Exception as e:
        st.error(f"Error al inicializar el agente RAG: {e}")
        st.info("Asegúrate de configurar correctamente la variable OPENAI_API_KEY en tu archivo .env")
        st.stop()

    # Inicialización del historial de chat en session_state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "¡Hola! Soy el asistente técnico oficial de **LLS Electric**. ¿En qué puedo ayudarte hoy sobre variadores, códigos de error o equivalencias de catálogo?",
            }
        ]

    # Renderizar el historial de chat existente
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de consulta por parte del usuario
    if prompt := st.chat_input("Consulta manuales técnicos, fallas (OCT, OVT, ETH, NTC) o reemplazos..."):
        # Agregar mensaje del usuario al estado y a la UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Enviar la consulta al agente y renderizar respuesta
        with st.chat_message("assistant"):
            with st.spinner("Consultando la base de conocimiento LLS Electric..."):
                try:
                    response = agent.chat(prompt)
                    response_text = str(response)
                except Exception as e:
                    # Si OpenAI o el RAG falla por cuota (429), usar el engine de fallback de Gemini/LS Electric
                    from src.core.agent import FallbackAgentWrapper
                    fallback_agent = FallbackAgentWrapper()
                    response_text = fallback_agent.chat(prompt)

                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})



if __name__ == "__main__":
    main()
