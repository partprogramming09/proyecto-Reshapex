import asyncio
from typing import Union, Optional

from config.settings import get_settings
from config.llm_factory import LLMFactory
from src.core.prompts import SYSTEM_PROMPT_AGENT
from src.core.agent import FallbackAgentWrapper
from src.tools.rag_tools import get_knowledge_tool, get_web_search_tool
from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.llms import ChatMessage, MessageRole


from src.core.memory import AgentMemoryManager


class ReActAgentWrapper:
    """Wrapper para ReActAgent de LlamaIndex con gestión modular de memoria a corto plazo via AgentMemoryManager."""

    def __init__(self, tools, llm, system_prompt: str, token_limit: int = 3000):
        self.memory_manager = AgentMemoryManager(token_limit=token_limit)
        self.agent = ReActAgent(
            tools=tools,
            llm=llm,
            system_prompt=system_prompt,
            verbose=True,
        )

    def chat(self, message: str) -> str:
        """Procesa una consulta del usuario manteniendo el historial de conversación con AgentMemoryManager.

        Args:
            message: Mensaje de consulta del usuario.

        Returns:
            Respuesta generada por el agente con memoria de contexto.
        """
        chat_history = self.memory_manager.get_history()

        async def _run():
            handler = self.agent.run(user_msg=message, chat_history=chat_history)
            return await handler

        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                res = loop.run_until_complete(_run())
            else:
                res = asyncio.run(_run())
        except Exception as e:
            print(f"[Info] Error en ejecución de ReActAgent, ejecutando directo: {e}")
            res = asyncio.run(_run())

        response_text = res.response.content if hasattr(res, "response") else str(res)

        self.memory_manager.add_user_message(message)
        self.memory_manager.add_assistant_message(response_text)

        return response_text


class AgentFactory:
    """Factory para construir agentes RAG de LS Electric."""

    @staticmethod
    def build_agent(api_key: Optional[str] = None) -> Union[ReActAgentWrapper, FallbackAgentWrapper]:
        """Construye agente con herramientas RAG, memoria ChatMemoryBuffer y system prompt.

        Args:
            api_key: API key de Gemini (opcional, usa settings si no se provee).

        Returns:
            ReActAgentWrapper con ChatMemoryBuffer si hay herramientas, FallbackAgentWrapper como fallback.
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
                agent = ReActAgentWrapper(
                    tools=tools,
                    llm=llm,
                    system_prompt=SYSTEM_PROMPT_AGENT,
                    token_limit=3000,
                )
                return agent
            else:
                print("[Info] Sin herramientas RAG. Usando FallbackAgentWrapper.")
                return FallbackAgentWrapper(api_key=gemini_key)

        except Exception as e:
            print(f"[Info] Transicionando a motor Fallback por error: {e}")
            return FallbackAgentWrapper(api_key=gemini_key)
