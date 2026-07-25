"""
Engine del Agente IA para LS Electric (Hackathon AgentSprint - ReshapeX)
Respuesta 100% independiente del Modelo LLM sin respuestas predeterminadas en código.
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
        self.client_genai = None
        self.client_generativeai = None

        if self.api_key and not self.api_key.startswith("tu_"):
            # Intentar cargar SDK moderno google-genai
            try:
                from google import genai
                self.client_genai = genai.Client(api_key=self.api_key)
            except Exception:
                pass

            # Intentar cargar SDK google-generativeai
            try:
                import google.generativeai as g_genai
                g_genai.configure(api_key=self.api_key)
                self.client_generativeai = g_genai
            except Exception:
                pass

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

        # 1. Intentar con SDK moderno google-genai
        if self.client_genai:
            for model_name in ['gemini-2.0-flash', 'gemini-1.5-flash-latest', 'gemini-2.5-flash']:
                try:
                    response = self.client_genai.models.generate_content(
                        model=model_name,
                        contents=system_prompt,
                    )
                    if response and response.text:
                        return {
                            "query": query,
                            "etapa_3_respuesta_limpia": response.text
                        }
                except Exception as e:
                    print(f"[Info] google-genai con modelo {model_name} no disponible: {e}")

        # 2. Intentar con SDK google-generativeai
        if self.client_generativeai:
            for model_name in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash-exp', 'gemini-pro']:
                try:
                    model = self.client_generativeai.GenerativeModel(model_name)
                    response = model.generate_content(system_prompt)
                    if response and response.text:
                        return {
                            "query": query,
                            "etapa_3_respuesta_limpia": response.text
                        }
                except Exception as e:
                    print(f"[Info] google-generativeai con modelo {model_name} no disponible: {e}")

        # 3. Si no hay API Key o la conexión falla
        return {
            "query": query,
            "etapa_3_respuesta_limpia": (
                "⚠️ **No se pudo conectar con la API del modelo de IA**\n\n"
                "Por favor verifica que la variable `GEMINI_API_KEY` esté configurada correctamente en tu archivo `.env`."
            )
        }
