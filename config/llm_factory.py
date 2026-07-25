from typing import Optional

from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

from config.settings import get_settings


class LLMFactory:
    """Factory para instanciar LLMs y embed models de Google Gemini."""

    @staticmethod
    def get_llm(temperature: float = 0.1) -> GoogleGenAI:
        """Retorna LLM de Google Gemini con configuración del settings.

        Args:
            temperature: Temperatura para generación (0.0-1.0).

        Returns:
            Instancia de GoogleGenAI configurada.

        Raises:
            ValueError: Si GEMINI_API_KEY no está configurada.
        """
        settings = get_settings()
        api_key = settings["gemini_api_key"]
        model_name = settings["llm_model"]

        if not api_key:
            raise ValueError("GEMINI_API_KEY no configurada en .env")

        return GoogleGenAI(
            model=model_name,
            api_key=api_key,
            temperature=temperature,
        )

    @staticmethod
    def get_embed_model() -> GoogleGenAIEmbedding:
        """Retorna embed model de Google Gemini.

        Returns:
            Instancia de GoogleGenAIEmbedding configurada.

        Raises:
            ValueError: Si GEMINI_API_KEY no está configurada.
        """
        settings = get_settings()
        api_key = settings["gemini_api_key"]
        model_name = settings["embed_model"]

        if not api_key:
            raise ValueError("GEMINI_API_KEY no configurada en .env")

        return GoogleGenAIEmbedding(
            model_name=model_name,
            api_key=api_key,
        )
