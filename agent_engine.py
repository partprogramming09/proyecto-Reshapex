"""
Engine del Agente IA para LS Electric (Hackathon AgentSprint - ReshapeX)
Respuesta 100% independiente del Modelo LLM (sin datos predeterminados en código).
"""

import os
from typing import Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class LSElectricAgentEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None

        if self.api_key and not self.api_key.startswith("tu_"):
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[Warning] No se pudo inicializar el cliente de Gemini: {e}")

    def procesar_consulta(self, query: str) -> Dict[str, Any]:
        """Procesa la consulta del usuario de forma independiente utilizando únicamente el modelo LLM."""
        
        system_prompt = f"""
        Eres un Ingeniero Experto Senior en Automatización Industrial y Soporte Técnico de LS Electric.
        Responde a la siguiente consulta del usuario de manera 100% independiente, clara, precisa y técnica:

        Consulta del Usuario: "{query}"

        FORMATO OBLIGATORIO DE RESPUESTA EN MARKDOWN:
        ### 🛠️ Diagnóstico Técnico LS Electric
        [Explicación técnica detallada y pasos de solución recomendados directamente para la consulta]

        ---

        ### ⚙️ Recomendación de Variante y Reemplazo de Equipo
        [Sugerencias de modelos o variantes de LS Electric aplicables a la consulta]

        ---

        ### 📑 Cita Oficial y Referencia Técnica
        > **Referencia:** Documentación y Especificaciones Oficiales de LS Electric  
        > *Respuesta generada dinámicamente por el modelo de IA.*
        """

        if not self.client:
            # Si no hay cliente Gemini inicializado con API Key válida
            return {
                "query": query,
                "etapa_3_respuesta_limpia": (
                    "⚠️ **Clave API de Gemini No Detectada**\n\n"
                    "Para obtener respuestas independientes del modelo en tiempo real, ingresa tu `GEMINI_API_KEY` en el archivo `.env` o en la barra lateral de Streamlit.\n\n"
                    "*(Obtén una clave gratuita sin tarjeta de crédito en [Google AI Studio](https://aistudio.google.com/))*"
                )
            }

        # Invocar el modelo Gemini de forma independiente
        for model_name in ['gemini-2.0-flash', 'gemini-1.5-flash']:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=system_prompt,
                )
                if response and response.text:
                    return {
                        "query": query,
                        "etapa_3_respuesta_limpia": response.text
                    }
            except Exception as e:
                print(f"[Info] Error consultando el modelo {model_name}: {e}")

        return {
            "query": query,
            "etapa_3_respuesta_limpia": (
                "❌ **Error al consultar el modelo de IA**\n\n"
                "Por favor verifica tu conexión a internet o la validez de tu `GEMINI_API_KEY`."
            )
        }
