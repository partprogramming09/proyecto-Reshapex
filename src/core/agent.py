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
    """Construye e inicializa el Agente RAG para LS Electric.
    Si la clave de OpenAI es inválida (401), sin saldo (429) o no funciona,
    retorna automáticamente el FallbackAgentWrapper sin lanzar excepciones.
    """
    try:
        settings = get_settings()
        openai_key = settings.get("openai_api_key", "")
        gemini_key = os.getenv("GEMINI_API_KEY", "")

        # Intentar usar OpenAI solo si hay una clave configurada
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
                print(f"[Info] Error al inicializar OpenAI ({e}). Usando motor Fallback de Gemini.")
                return FallbackAgentWrapper(api_key=gemini_key)

        return FallbackAgentWrapper(api_key=gemini_key)
    except Exception as general_error:
        print(f"[Warning] Error general en build_agent ({general_error}). Usando motor Fallback por defecto.")
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        return FallbackAgentWrapper(api_key=gemini_key)
