import os
from typing import Optional, Union, Any

from config.settings import get_settings
from src.rag.indexer import load_or_create_index, has_documents
from src.core.engine import LSElectricAgentEngine


from src.core.memory import AgentMemoryManager


class FallbackAgentWrapper:
    """Wrapper que usa LSElectricAgentEngine con contexto RAG opcional y AgentMemoryManager.

    Se utiliza como fallback cuando ReActAgent no puede construirse.
    """

    def __init__(self, api_key: Optional[str] = None, token_limit: int = 3000):
        """Inicializa el wrapper.

        Args:
            api_key: API key de Gemini (opcional).
            token_limit: Límite de tokens de entrada para el buffer de memoria.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._rag_context = None
        self._rag_loaded = False
        self.memory_manager = AgentMemoryManager(token_limit=token_limit)

    def _load_rag_context(self) -> Union[Any, bool]:
        """Carga el contexto RAG si hay documentos disponibles.

        Returns:
            QueryEngine si hay documentos, False de lo contrario.
        """
        if self._rag_loaded:
            return self._rag_context
        self._rag_loaded = True
        try:
            if not has_documents():
                print("[RAG] Sin documentos. Modo autónomo.")
                self._rag_context = False
                return False
            index = load_or_create_index()
            if index is None:
                self._rag_context = False
                return False
            settings = get_settings()
            query_engine = index.as_query_engine(
                similarity_top_k=settings["similarity_top_k"]
            )
            self._rag_context = query_engine
            return self._rag_context
        except Exception as e:
            print(f"[Info] No se pudo cargar RAG: {e}")
            self._rag_context = False
            return False

    def chat(self, message: str) -> str:
        """Procesa un mensaje del usuario utilizando AgentMemoryManager para recordar el contexto.

        Args:
            message: Mensaje del usuario.

        Returns:
            Respuesta del agente.
        """
        rag = self._load_rag_context()
        rag_context = ""

        if rag:
            try:
                rag_response = rag.query(message)
                if rag_response and str(rag_response).strip():
                    rag_context = f"\n\n[CONOCIMIENTO DE MANUALES LS ELECTRIC]:\n{rag_response}"
            except Exception as e:
                print(f"[Info] Error en consulta RAG: {e}")

        engine = LSElectricAgentEngine(api_key=self.api_key)

        if rag_context:
            engine._rag_context = rag_context

        history_str = self.memory_manager.get_formatted_history_text(max_turns=4)
        history_context = f"[HISTORIAL RECIENTE CONVERSACIÓN]:\n{history_str}\n\n" if history_str else ""

        query_with_history = f"{history_context}{message}" if history_context else message
        result = engine.process_query(query_with_history)
        response = result["clean_response"]

        self.memory_manager.add_user_message(message)
        self.memory_manager.add_assistant_message(response)
        return response
