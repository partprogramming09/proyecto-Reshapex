from typing import Union, Optional

from config.settings import get_settings
from config.llm_factory import LLMFactory
from src.core.prompts import SYSTEM_PROMPT_AGENT
from src.core.agent import FallbackAgentWrapper
from src.tools.rag_tools import get_knowledge_tool, get_web_search_tool
from llama_index.core import Settings
from llama_index.core.agent import ReActAgent


class AgentFactory:
    """Factory para construir agentes RAG de LS Electric."""

    @staticmethod
    def build_agent(api_key: Optional[str] = None) -> Union["ReActAgent", FallbackAgentWrapper]:
        """Construye agente con herramientas RAG y system prompt.

        Args:
            api_key: API key de Gemini (opcional, usa settings si no se provee).

        Returns:
            ReActAgent si hay herramientas disponibles, FallbackAgentWrapper como fallback.
        """
        settings = get_settings()
        gemini_key = api_key or settings.get("gemini_api_key", "")

        if not gemini_key:
            print("[Info] Sin API key. Usando FallbackAgentWrapper.")
            return FallbackAgentWrapper(api_key=gemini_key)

        try:
            llm = LLMFactory.get_llm(temperature=0.1)
            embed_model = LLMFactory.get_embed_model()

            Settings.llm = llm
            Settings.embed_model = embed_model

            knowledge_tool = get_knowledge_tool()
            web_tool = get_web_search_tool()

            tools = []
            if knowledge_tool:
                tools.append(knowledge_tool)
            if web_tool:
                tools.append(web_tool)

            if tools:
                agent = ReActAgent.from_tools(
                    tools=tools,
                    llm=llm,
                    verbose=True,
                    system_prompt=SYSTEM_PROMPT_AGENT,
                )
                return agent
            else:
                print("[Info] Sin herramientas RAG. Usando FallbackAgentWrapper.")
                return FallbackAgentWrapper(api_key=gemini_key)

        except Exception as e:
            print(f"[Info] Transicionando a motor Fallback por error: {e}")
            return FallbackAgentWrapper(api_key=gemini_key)
