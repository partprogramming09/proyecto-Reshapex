import streamlit as st

from config.settings import get_settings
from src.core.agent import FallbackAgentWrapper
from src.core.agent_factory import AgentFactory
from ui.sidebar import render_sidebar
from ui.chat import render_chat


@st.cache_resource
def get_cached_agent():
    """Construye y cachea el agente RAG."""
    return AgentFactory.build_agent()


def main():
    """Funcion principal de la aplicacion Streamlit."""
    st.set_page_config(
        page_title="LS Electric AI",
        page_icon="⚡",
        layout="wide",
    )

    settings = get_settings()
    settings["data_raw_dir"].mkdir(parents=True, exist_ok=True)

    render_sidebar()

    try:
        agent = get_cached_agent()
    except Exception:
        agent = FallbackAgentWrapper()

    render_chat(agent)


if __name__ == "__main__":
    main()
