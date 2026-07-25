import streamlit as st


def apply_custom_theme() -> None:
    """Inyecta el sistema de diseño CSS global para la interfaz LS Electric AI."""
    custom_css = """
    <style>
    /* Estilos globales */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Estilos del Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #14171D !important;
        border-right: 1px solid #232730;
    }

    /* Botones primarios y secundarios */
    .stButton > button {
        border-radius: 8px !important;
        border: 1px solid #333945 !important;
        background-color: #1E232B !important;
        color: #E2E8F0 !important;
        transition: all 0.2s ease-in-out !important;
        font-weight: 500 !important;
    }
    .stButton > button:hover {
        border-color: #FFD700 !important;
        color: #FFD700 !important;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.2) !important;
        transform: translateY(-1px) !important;
    }

    /* Tarjetas y Expanders de 3 Etapas */
    div[data-testid="stExpander"] {
        background-color: #171B22 !important;
        border: 1px solid #272C36 !important;
        border-radius: 10px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
    }
    div[data-testid="stExpander"] summary {
        font-weight: 600 !important;
        color: #FFD700 !important;
    }

    /* Badges de Estado RAG */
    .rag-badge-active {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(6, 95, 70, 0.3));
        border: 1px solid #10B981;
        color: #34D399;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .rag-badge-autonomous {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(30, 58, 138, 0.3));
        border: 1px solid #3B82F6;
        color: #60A5FA;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Input de Chat */
    div[data-testid="stChatInput"] input {
        border-radius: 10px !important;
        border: 1px solid #333945 !important;
        background-color: #171B22 !important;
        color: #FFFFFF !important;
    }
    div[data-testid="stChatInput"] input:focus {
        border-color: #FFD700 !important;
        box-shadow: 0 0 8px rgba(255, 215, 0, 0.3) !important;
    }

    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0E1117;
    }
    ::-webkit-scrollbar-thumb {
        background: #272C36;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #FFD700;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_status_badge(is_rag: bool, doc_count: int = 0) -> None:
    """Renderiza un badge de estado del sistema (Modo RAG vs Modo Autónomo)."""
    if is_rag and doc_count > 0:
        html = f"""
        <div class="rag-badge-active">
            <span>🟢</span> Modo RAG Activo ({doc_count} documento{'s' if doc_count > 1 else ''})
        </div>
        """
    else:
        html = """
        <div class="rag-badge-autonomous">
            <span>⚡</span> Modo Autónomo (Gemini 3.1 Flash Lite)
        </div>
        """
    st.markdown(html, unsafe_allow_html=True)
