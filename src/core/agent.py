import os
import sys
from pathlib import Path

# Asegurar la ruta raíz en sys.path
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from config.settings import get_settings


class FallbackAgentWrapper:
    """Wrapper compatible con la interfaz agent.chat() que utiliza el engine LSElectricAgentEngine."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    def chat(self, message: str) -> str:
        from agent_engine import LSElectricAgentEngine
        engine = LSElectricAgentEngine(api_key=self.api_key)
        res = engine.procesar_consulta(message)
        return res["etapa_3_respuesta_limpia"]


def build_agent():
    """Construye e inicializa el Agente RAG para LS Electric.
    Si OpenAI no está disponible o falla por cualquier razón,
    retorna automáticamente un FallbackAgentWrapper funcional.
    """
    try:
        settings = get_settings()
        openai_key = settings.get("openai_api_key", "")
        gemini_key = os.getenv("GEMINI_API_KEY", "")

        # Intentar usar OpenAI solo si hay una clave configurada que empieza por sk-
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
                print(f"[Info] Transicionando a motor Fallback de Gemini por error en OpenAI: {e}")
                return FallbackAgentWrapper(api_key=gemini_key)

        return FallbackAgentWrapper(api_key=gemini_key)
    except Exception as general_error:
        print(f"[Warning] Error general al construir el agente ({general_error}). Usando motor Fallback.")
        return FallbackAgentWrapper()
