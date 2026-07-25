import os
import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from config.settings import get_settings
from agent_engine import LSElectricAgentEngine


class FallbackAgentWrapper:
    """Wrapper compatible con la interfaz agent.chat() que utiliza el engine LSElectricAgentEngine."""

    def __init__(self, api_key: str = None):
        self.engine = LSElectricAgentEngine(api_key=api_key)

    def chat(self, message: str):
        res = self.engine.procesar_consulta(message)
        return res["etapa_3_respuesta_limpia"]


def build_agent():
    """Construye e inicializa el Agente RAG para LS Electric con soporte inteligente para OpenAI y Gemini."""
    settings = get_settings()
    openai_key = settings.get("openai_api_key", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    # Intentar usar OpenAI si hay una clave configurada que parece válida
    if openai_key and openai_key.startswith("sk-"):
        try:
            from src.tools.rag_tools import get_lls_knowledge_tool
            from llama_index.core import Settings
            from llama_index.core.agent import ReActAgent
            from llama_index.llms.openai import OpenAI
            from llama_index.embeddings.openai import OpenAIEmbedding

            llm = OpenAI(
                model=settings["llm_model"],
                api_key=openai_key,
                temperature=0.1,
            )
            embed_model = OpenAIEmbedding(
                model_name=settings["embed_model"],
                api_key=openai_key,
            )

            Settings.llm = llm
            Settings.embed_model = embed_model

            knowledge_tool = get_lls_knowledge_tool()

            agent = ReActAgent.from_tools(
                tools=[knowledge_tool],
                llm=llm,
                verbose=True,
            )
            return agent
        except Exception as e:
            print(f"[Info] Transicionando a engine Gemini/LS Electric por error de OpenAI ({e})")

    # Fallback automático a Gemini / Engine Oficial LS Electric (100% Gratis sin Tarjeta)
    return FallbackAgentWrapper(api_key=gemini_key)
