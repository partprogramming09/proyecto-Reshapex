"""
Engine del Agente IA para LS Electric (Hackathon AgentSprint - ReshapeX)
Pipeline de 3 etapas: Diagnóstico → Variantes → Respuesta Grounded con Cita.
Funciona de manera autónoma (Gemini) o con contexto RAG (PDFs del usuario).
"""

import os
import time
import hashlib
import re
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)
except Exception as e:
    print(f"[Warning] Error al cargar .env: {e}")


class LSElectricAgentEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.client_genai = None
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._last_request_time: float = 0
        self._min_interval: float = 2.0
        self._rag_context: Optional[str] = None

        if self.api_key and not self.api_key.startswith("tu_"):
            try:
                from google import genai
                self.client_genai = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[Info] No se pudo inicializar google-genai: {e}")

    def _cache_key(self, query: str) -> str:
        return hashlib.md5(query.strip().lower().encode()).hexdigest()

    def _get_cached(self, query: str) -> Optional[str]:
        key = self._cache_key(query)
        entry = self._cache.get(key)
        if entry and (time.time() - entry["ts"]) < 300:
            return entry["response"]
        if entry:
            del self._cache[key]
        return None

    def _set_cached(self, query: str, response: str):
        key = self._cache_key(query)
        self._cache[key] = {"response": response, "ts": time.time()}
        if len(self._cache) > 50:
            oldest = min(self._cache, key=lambda k: self._cache[k]["ts"])
            del self._cache[oldest]

    def _throttle(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

    def _validar_entrada(self, query: str) -> Optional[str]:
        if not query or not query.strip():
            return "La consulta no puede estar vacía."
        if len(query) > 500:
            return "La consulta excede el límite de 500 caracteres."
        return None

    def _construir_prompt_etapas(self, query: str) -> str:
        rag_bloque = ""
        instruccion_rag = ""

        if self._rag_context:
            rag_bloque = f"\n\n[INFORMACIÓN DE MANUALES Y DOCUMENTACIÓN LS ELECTRIC]:\n{self._rag_context}"
            instruccion_rag = (
                "Usa la información de los manuales como FUENTE PRIMARIA de tu respuesta. "
                "Cita el documento, sección y página cuando sea posible."
            )
        else:
            instruccion_rag = (
                "Responde con tu conocimiento general sobre automatización industrial y equipos LS Electric. "
                "Si no tienes información específica, indica qué datos adicionales se necesitan."
            )

        prompt = f"""Eres un Ingeniero Experto Senior en Automatización Industrial y Soporte Técnico de LS Electric.
{rag_bloque}

{instruccion_rag}

Responde en EXACTAMENTE estas 3 etapas:

ETAPA 1 - DIAGNÓSTICO TÉCNICO:
Identifica el problema o consulta del usuario. Explica la causa probable y lista las acciones correctivas paso a paso.

ETAPA 2 - RECOMENDACIÓN:
Si aplica, recomienda equipos, variantes o soluciones específicas. Especifica compatibilidad, potencia, voltaje y dimensiones.

ETAPA 3 - CITA DE ORIGEN:
Termina SIEMPRE con la fuente de información. Si la información viene de un documento cargado, cita:
📑 **Fuente:** [Nombre del documento], [Sección/Página]
Si la información es de conocimiento general, indica:
📑 **Fuente:** Conocimiento general de ingeniería industrial

Consulta del usuario: "{query}"
"""
        return prompt

    def procesar_consulta(self, query: str) -> Dict[str, Any]:
        error_validacion = self._validar_entrada(query)
        if error_validacion:
            return {"query": query, "etapa_3_respuesta_limpia": f"⚠️ {error_validacion}"}

        cached = self._get_cached(query)
        if cached:
            print("[Cache] Respuesta servida desde caché")
            return {"query": query, "etapa_3_respuesta_limpia": cached}

        prompt = self._construir_prompt_etapas(query)

        if self.client_genai:
            models_to_try = ['gemini-3.1-flash-lite', 'gemini-3.5-flash-lite', 'gemma-4-26b-a4b-it']
            errors_by_type = {"auth": None, "quota": None, "not_found": None, "other": None}

            for model_name in models_to_try:
                for attempt in range(2):
                    try:
                        self._throttle()
                        response = self.client_genai.models.generate_content(
                            model=model_name,
                            contents=prompt,
                        )
                        if response and response.text:
                            respuesta = response.text
                            self._set_cached(query, respuesta)
                            return {"query": query, "etapa_3_respuesta_limpia": respuesta}
                    except Exception as e:
                        error_msg = str(e)
                        print(f"[Info] Error en google-genai ({model_name}, intento {attempt + 1}): {e}")

                        if 'API_KEY_INVALID' in error_msg or 'PERMISSION_DENIED' in error_msg or 'UNAUTHENTICATED' in error_msg:
                            errors_by_type["auth"] = error_msg
                            break
                        if 'RESOURCE_EXHAUSTED' in error_msg or '429' in error_msg:
                            errors_by_type["quota"] = error_msg
                            break
                        if 'NOT_FOUND' in error_msg or '404' in error_msg:
                            errors_by_type["not_found"] = error_msg
                            break
                        errors_by_type["other"] = error_msg

                        if attempt == 0:
                            print("[Info] Reintentando en 3s...")
                            time.sleep(3)

                    if errors_by_type["auth"] or errors_by_type["quota"] or errors_by_type["not_found"]:
                        break

                if errors_by_type["auth"] or errors_by_type["quota"]:
                    break

            return {"query": query, "etapa_3_respuesta_limpia": self._generar_mensaje_error(errors_by_type)}

        return {"query": query, "etapa_3_respuesta_limpia": (
            "⚠️ **No se configuró la GEMINI_API_KEY**\n\n"
            "Agrega tu clave en `.env`:\n```env\nGEMINI_API_KEY=tu_clave\n```\n"
            "*(Obtén tu clave en [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey))*"
        )}

    def _generar_mensaje_error(self, errors: dict) -> str:
        if errors["auth"]:
            return (
                "⚠️ **GEMINI_API_KEY inválida**\n\n"
                "Genera una nueva clave en [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)\n"
                "y colócala en `.env`:\n```env\nGEMINI_API_KEY=tu_nueva_clave\n```"
            )
        if errors["quota"]:
            return (
                "⚠️ **Cuota de Gemini agotada (429)**\n\n"
                "Tu clave es válida pero la cuota se agotó.\n\n"
                "**Soluciones:**\n"
                "- Espera ~60s y vuelve a intentar.\n"
                "- Verifica tu uso en [aistudio.google.com](https://aistudio.google.com/app/apikey).\n"
                "- Habilita facturación en Google Cloud para mayor cuota."
            )
        if errors["not_found"]:
            return (
                "⚠️ **Modelo no disponible (404)**\n\n"
                "Verifica los modelos en [Google AI Studio](https://aistudio.google.com)."
            )
        error_str = errors.get("other", "Error desconocido")
        return (
            f"⚠️ **Error al conectar con Gemini**\n\nDetalle: {error_str[:200]}\n\n"
            "Verifica tu `.env` y conexión a internet."
        )
