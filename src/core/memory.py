from typing import List, Optional
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.llms import ChatMessage, MessageRole


class AgentMemoryManager:
    """Administrador modular de memoria a corto plazo para el Agente LS Electric.
    
    Encapsula ChatMemoryBuffer de LlamaIndex asegurando que el contexto histórico
    enviado al modelo LLM (gemini-3.1-flash-lite) respete el límite de tokens de entrada.
    """

    def __init__(self, token_limit: int = 3000):
        """Inicializa la memoria con un límite de tokens de entrada.

        Args:
            token_limit: Máximo de tokens permitidos para el historial en el prompt.
        """
        self.token_limit = token_limit
        self._buffer = ChatMemoryBuffer.from_defaults(token_limit=token_limit)

    def get_history(self) -> List[ChatMessage]:
        """Recupera la lista recortada de mensajes de la conversación según el token_limit.

        Returns:
            Lista de objetos ChatMessage procesados por ChatMemoryBuffer.
        """
        return self._buffer.get()

    def add_user_message(self, content: str) -> None:
        """Registra una consulta del usuario en el búfer de memoria.

        Args:
            content: Mensaje escrito por el usuario.
        """
        self._buffer.put(ChatMessage(role=MessageRole.USER, content=content))

    def add_assistant_message(self, content: str) -> None:
        """Registra la respuesta del asistente en el búfer de memoria.

        Args:
            content: Respuesta generada por el agente.
        """
        self._buffer.put(ChatMessage(role=MessageRole.ASSISTANT, content=content))

    def clear(self) -> None:
        """Limpia todo el historial de la sesión."""
        self._buffer.reset()

    def get_formatted_history_text(self, max_turns: int = 4) -> str:
        """Formatea el historial reciente como texto plano (útil para fallback engines).

        Args:
            max_turns: Número máximo de turnos recientes a incluir.

        Returns:
            String formateado con el historial.
        """
        history = self.get_history()
        if not history:
            return ""
        recent = history[-max_turns:]
        lines = []
        for msg in recent:
            role_label = "USUARIO" if msg.role == MessageRole.USER else "ASISTENTE"
            lines.append(f"{role_label}: {msg.content}")
        return "\n".join(lines)
