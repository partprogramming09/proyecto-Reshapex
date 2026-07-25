import os
import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from config.settings import get_settings
from src.core.prompts import SYSTEM_PROMPT_AGENT


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
    """Construye el Agente RAG con prioridad a data local y web como complemento."""
    try:
        settings = get_settings()
        gemini_key = settings.get("gemini_api_key", "")

        if gemini_key:
            try:
                from src.tools.rag_tools import get_lls_knowledge_tool, get_web_search_tool
                from llama_index.core import Settings
                from llama_index.core.agent import ReActAgent
                from llama_index.llms.google_genai import GoogleGenAI
                from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

                llm = GoogleGenAI(
                    model=settings["llm_model"],
                    api_key=gemini_key,
                    temperature=0.1,
                )
                embed_model = GoogleGenAIEmbedding(
                    model_name=settings["embed_model"],
                    api_key=gemini_key,
                )

                Settings.llm = llm
                Settings.embed_model = embed_model

                knowledge_tool = get_lls_knowledge_tool()
                web_tool = get_web_search_tool()

                agent = ReActAgent.from_tools(
                    tools=[knowledge_tool, web_tool],
                    llm=llm,
                    verbose=True,
                    system_prompt=SYSTEM_PROMPT_AGENT,
                )
                return agent
            except Exception as e:
                print(f"[Info] Transicionando a motor Fallback por error: {e}")
                return FallbackAgentWrapper(api_key=gemini_key)

        return FallbackAgentWrapper(api_key=gemini_key)
    except Exception as general_error:
        print(f"[Warning] Error general al construir el agente ({general_error}). Usando motor Fallback.")
        return FallbackAgentWrapper()
