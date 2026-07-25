"""
Engine del Agente IA para LS Electric (Hackathon AgentSprint - ReshapeX)
Pipeline de 3 etapas: Diagnóstico → Variantes → Respuesta Grounded con Cita.
Funciona de manera autónoma (Gemini) o con contexto RAG (PDFs del usuario).
"""

import os
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)
except Exception as e:
    print(f"[Warning] Error al cargar .env: {e}")


class RateLimiterService:
    """Servicio desacoplado para control de tasa de solicitudes (SRP)."""

    def __init__(self, min_interval_seconds: float = 2.0):
        self.min_interval = min_interval_seconds
        self._last_request_time: float = 0

    def throttle(self) -> None:
        """Asegura un tiempo mínimo de espera entre solicitudes."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_request_time = time.time()


class ResponseCacheService:
    """Servicio desacoplado de almacenamiento en caché en memoria (SRP)."""

    def __init__(self, ttl_seconds: int = 300, max_size: int = 50):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._store: Dict[str, Dict[str, Any]] = {}

    def generate_key(self, query: str) -> str:
        """Genera hash MD5 de la consulta para usar como clave."""
        return hashlib.md5(query.strip().lower().encode()).hexdigest()

    def get(self, query: str) -> Optional[str]:
        """Obtiene la respuesta cacheada si aún es válida por TTL."""
        key = self.generate_key(query)
        entry = self._store.get(key)
        if entry and (time.time() - entry["ts"]) < self.ttl_seconds:
            return entry["response"]
        if entry:
            del self._store[key]
        return None

    def set(self, query: str, response: str) -> None:
        """Almacena una respuesta en la caché limitando el tamaño máximo."""
        key = self.generate_key(query)
        self._store[key] = {"response": response, "ts": time.time()}
        if len(self._store) > self.max_size:
            oldest_key = min(self._store, key=lambda k: self._store[k]["ts"])
            del self._store[oldest_key]


class LSElectricAgentEngine:
    """Engine principal del Agente IA de LS Electric aplicando 3 etapas secuenciales."""

    MAX_QUERY_LENGTH: int = 4000
    FALLBACK_MODELS = [
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash-lite",
        "gemma-4-26b-a4b-it",
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.client_genai = None
        self._rag_context: Optional[str] = None

        # Servicios desacoplados (SRP)
        self.rate_limiter = RateLimiterService(min_interval_seconds=2.0)
        self.cache_service = ResponseCacheService(ttl_seconds=300, max_size=50)

        if self.api_key and not self.api_key.startswith("tu_"):
            try:
                from google import genai
                self.client_genai = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[Info] No se pudo inicializar google-genai: {e}")

    def _cache_key(self, query: str) -> str:
        """Compatibilidad retrospectiva para clave de caché."""
        return self.cache_service.generate_key(query)

    def _get_cached(self, query: str) -> Optional[str]:
        """Compatibilidad retrospectiva para obtener caché."""
        return self.cache_service.get(query)

    def _set_cached(self, query: str, response: str) -> None:
        """Compatibilidad retrospectiva para guardar caché."""
        self.cache_service.set(query, response)

    def _throttle(self) -> None:
        """Compatibilidad retrospectiva para throttling."""
        self.rate_limiter.throttle()

    def _validate_input(self, query: str) -> Optional[str]:
        if not query or not query.strip():
            return "La consulta no puede estar vacía."
        if len(query) > self.MAX_QUERY_LENGTH:
            return f"La consulta excede el límite de {self.MAX_QUERY_LENGTH} caracteres."
        return None

    def _build_stage_prompt(self, query: str) -> str:
        rag_block = ""
        rag_instruction = ""

        if self._rag_context:
            rag_block = f"\n\n[INFORMACIÓN DE MANUALES Y DOCUMENTACIÓN LS ELECTRIC]:\n{self._rag_context}"
            rag_instruction = (
                "Usa la información de los manuales como FUENTE PRIMARIA de tu respuesta. "
                "Cita el documento, sección y página cuando sea posible."
            )
        else:
            rag_instruction = (
                "Responde con tu conocimiento general sobre automatización industrial y equipos LS Electric. "
                "Si no tienes información específica, indica qué datos adicionales se necesitan."
            )

        prompt = f"""Eres un Ingeniero Experto Senior en Automatización Industrial y Soporte Técnico de LS Electric.
{rag_block}

{rag_instruction}

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

    def process_query(self, query: str) -> Dict[str, Any]:
        validation_error = self._validate_input(query)
        if validation_error:
            return {"query": query, "clean_response": f"⚠️ {validation_error}"}

        cached = self.cache_service.get(query)
        if cached:
            print("[Cache] Respuesta servida desde caché")
            return {"query": query, "clean_response": cached}

        prompt = self._build_stage_prompt(query)

        if self.client_genai:
            errors_by_type = {"auth": None, "quota": None, "not_found": None, "other": None}

            for model_name in self.FALLBACK_MODELS:
                for attempt in range(2):
                    try:
                        self.rate_limiter.throttle()
                        response = self.client_genai.models.generate_content(
                            model=model_name,
                            contents=prompt,
                        )
                        if response and response.text:
                            answer = response.text
                            self.cache_service.set(query, answer)
                            return {"query": query, "clean_response": answer}
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

            return {"query": query, "clean_response": self._generate_error_message(errors_by_type)}

        return {"query": query, "clean_response": (
            "⚠️ **No se configuró la GEMINI_API_KEY**\n\n"
            "Agrega tu clave en `.env`:\n```env\nGEMINI_API_KEY=tu_clave\n```\n"
            "*(Obtén tu clave en [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey))*"
        )}

    def _generate_error_message(self, errors: dict) -> str:
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
