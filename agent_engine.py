"""
Engine del Agente IA para LS Electric (Hackathon AgentSprint - ReshapeX)
Carga explícita de .env y generación con el SDK oficial google-genai / google-generativeai.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Cargar .env explícitamente desde la raíz del proyecto
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)
except Exception as e:
    print(f"[Warning] Error al cargar .env: {e}")


class LSElectricAgentEngine:
    def __init__(self, api_key: str = None):
        # Obtener API Key de argumento o de variable de entorno GEMINI_API_KEY
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.client_genai = None
        self.client_generativeai = None

        if self.api_key and not self.api_key.startswith("tu_"):
            # Intentar inicializar SDK moderno google-genai
            try:
                from google import genai
                self.client_genai = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[Info] No se pudo inicializar google-genai: {e}")

            # Intentar inicializar SDK google-generativeai
            try:
                import google.generativeai as g_genai
                g_genai.configure(api_key=self.api_key)
                self.client_generativeai = g_genai
            except Exception as e:
                print(f"[Info] No se pudo inicializar google-generativeai: {e}")

    def procesar_consulta(self, query: str) -> Dict[str, Any]:
        """Procesa la consulta del usuario utilizando el modelo de IA de Gemini."""

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

        # 1. Probar con SDK moderno google-genai
        if self.client_genai:
            for model_name in ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']:
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
                    print(f"[Info] Error en google-genai ({model_name}): {e}")

        # 2. Probar con SDK google-generativeai
        if self.client_generativeai:
            for model_name in ['gemini-1.5-flash', 'gemini-2.0-flash-exp', 'gemini-1.5-pro']:
                try:
                    model = self.client_generativeai.GenerativeModel(model_name)
                    response = model.generate_content(system_prompt)
                    if response and response.text:
                        return {
                            "query": query,
                            "etapa_3_respuesta_limpia": response.text
                        }
                except Exception as e:
                    print(f"[Info] Error en google-generativeai ({model_name}): {e}")

        # Si no se pudo obtener respuesta del modelo
        return {
            "query": query,
            "etapa_3_respuesta_limpia": (
                "⚠️ **No se pudo autenticar la GEMINI_API_KEY**\n\n"
                "Asegúrate de colocar tu clave de Google AI Studio (que comienza con `AIzaSy...`) en tu archivo `.env`:\n\n"
                "```env\n"
                "GEMINI_API_KEY=AIzaSyTuClaveDeGoogleStudioAqui\n"
                "```\n\n"
                "*(Obtén tu clave gratuita en [aistudio.google.com](https://aistudio.google.com/app/apikey))*"
            )
        }
