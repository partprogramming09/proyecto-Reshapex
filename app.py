import streamlit as st

from config.settings import get_settings
from src.core.agent import FallbackAgentWrapper
from src.core.agent_factory import AgentFactory
from ui.theme import apply_custom_theme
from ui.sidebar import render_sidebar
from ui.chat import render_chat


@st.cache_resource
def get_cached_agent():
    """Construye y cachea el agente RAG."""
    return AgentFactory.build_agent()


def main():
    """Función principal de la aplicación Streamlit."""
    st.set_page_config(
        page_title="LS Electric AI — Diagnóstico Industrial",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inyección del tema visual personalizado (Dark Mode + LS Gold)
    apply_custom_theme()

    settings = get_settings()
    settings["data_raw_dir"].mkdir(parents=True, exist_ok=True)

    render_sidebar()

    try:
        agent = get_cached_agent()
    except Exception as e:
        print(f"[Info] Error al cargar agente cacheado: {e}")
        agent = FallbackAgentWrapper()

    render_chat(agent)


if __name__ == "__main__":
    main()
