import os
import time
import streamlit as st
from agent_engine import LSElectricAgentEngine

# Configuración de página de Streamlit
st.set_page_config(
    page_title="LS Electric - Asistente de Automatización IA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados CSS (Tema Oscuro ReshapeX / LS Electric)
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #73B400 0%, #00D9FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #A0AEB8;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .pipeline-card {
        background-color: #1C2128;
        border: 1px solid rgba(139,154,173,0.2);
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .badge-step {
        background-color: #73B400;
        color: #0D1117;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    .citation-box {
        background-color: rgba(0, 217, 255, 0.08);
        border-left: 4px solid #00D9FF;
        padding: 10px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://www.ls-electric.com/images/common/logo.png", width=180)
    st.markdown("---")
    st.subheader("⚙️ Configuración del Agente")
    
    api_key_input = st.text_input("Gemini API Key", type="password", help="Ingresa tu API Key de Google AI Studio")
    
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input
        st.success("API Key cargada correctamente 🟢")
    else:
        if os.getenv("GEMINI_API_KEY"):
            st.info("API Key detectada desde entorno (.env) 🟢")
        else:
            st.warning("Modo Demostración Local (Fallback activo) 🟡")

    st.markdown("---")
    st.subheader("💡 Consultas Rápidas de Prueba")
    preset = st.radio(
        "Selecciona un ejemplo:",
        [
            "Ninguno",
            "Error OCT en variador iG5A de 5.5kW",
            "Sobrevoltaje OVT al frenar el motor",
            "Sustituto para iG5A de 2.2kW 220V"
        ]
    )
    
    st.markdown("---")
    st.caption("AgentSprint Hackathon Medellín 2026 · Powered by ReshapeX")

# Header principal
st.markdown('<div class="main-title">⚡ LS Electric — AI Agent Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Asistente Inteligente de Diagnóstico, Variantes y Citas Técnicas para OEMs</div>', unsafe_allow_html=True)

# Inicializar motor
engine = LSElectricAgentEngine()

# Estado de chat
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "¡Hola! Soy tu asistente técnico oficial de **LS Electric**. Puedo ayudarte a diagnosticar códigos de error en variadores/PLCs, recomendar variantes de reemplazo y citar exactamente la página del manual oficial. ¿En qué te ayudo hoy?"
        }
    ]

# Renderizar historial de chat
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Determinar consulta del usuario (por preset o input)
user_query = None
if preset != "Ninguno":
    user_query = preset

prompt_input = st.chat_input("Escribe tu consulta sobre variadores, PLCs o códigos de falla LS Electric...")
if prompt_input:
    user_query = prompt_input

if user_query:
    # Agregar mensaje del usuario
    st.session_state["messages"].append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Procesar con el flujo de 3 etapas
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        
        with status_placeholder.container():
            st.markdown("⏳ **Ejecutando Flujo de Trabajo del Agente (3 Etapas)...**")
            progress_bar = st.progress(0)
            
            # Etapa 1: Consulta de Guía
            time.sleep(0.3)
            progress_bar.progress(33)
            st.caption("🔍 **Etapa 1:** Consultando Guías y Manuales Técnicos LS Electric...")
            res_etapa1 = engine.etapa_1_consultar_guia(user_query)
            
            # Etapa 2: Revisar Variantes
            time.sleep(0.3)
            progress_bar.progress(66)
            st.caption("⚙️ **Etapa 2:** Analizando Matriz de Variantes y Reemplazos de Producto...")
            res_etapa2 = engine.etapa_2_revisar_variantes(user_query)
            
            # Etapa 3: Generar Respuesta Limpia
            time.sleep(0.4)
            progress_bar.progress(100)
            st.caption("📑 **Etapa 3:** Generando Respuesta Fundamentada con Cita de Manual...")
            respuesta_limpia = engine.etapa_3_generar_respuesta_limpia(user_query, res_etapa1, res_etapa2)
            
        status_placeholder.empty()

        # Visualizador interactivo de las 3 etapas del agente en expedientes
        with st.expander("🛠️ Ver Traza del Agente (3 Etapas Internas)", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<span class="badge-step">ETAPA 1</span> **Guía Técnica**', unsafe_allow_html=True)
                st.json(res_etapa1["data"])
                
            with col2:
                st.markdown('<span class="badge-step">ETAPA 2</span> **Variantes / Reemplazo**', unsafe_allow_html=True)
                st.json(res_etapa2["data"])
                
            with col3:
                st.markdown('<span class="badge-step">ETAPA 3</span> **Cita de Origen**', unsafe_allow_html=True)
                st.info(f"📍 **Manual:** {res_etapa1['data'].get('manual_origen')}\n\n📖 **Pág:** {res_etapa1['data'].get('pagina')}")

        # Mostrar respuesta limpia final
        st.markdown(respuesta_limpia)
        st.session_state["messages"].append({"role": "assistant", "content": respuesta_limpia})
