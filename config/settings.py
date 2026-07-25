import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv


# Constants
SUPPORTED_EXTENSIONS: List[str] = [".pdf", ".txt", ".md"]
DEFAULT_CHUNK_SIZE: int = 1024
DEFAULT_CHUNK_OVERLAP: int = 20
DEFAULT_SIMILARITY_TOP_K: int = 4
DEFAULT_EMBEDDING_DIMENSION: int = 768
HASH_FILE_NAME: str = ".hash"
CACHE_TTL_SECONDS: int = 300
THROTTLE_MIN_INTERVAL: float = 2.0
MIN_QUERY_INTERVAL: int = 3
PRESETS: List[str] = [
    "Tengo un error OCT en mi variador iG5A de 5.5kW al acelerar",
    "¿Qué variador me recomiendan para reemplazar un iG5A de 2.2kW?",
    "Mi variador S100 muestra error OVT, ¿qué hago?",
    "¿Cuáles son las diferencias entre iG5A y H100?",
]


@lru_cache(maxsize=1)
def get_settings() -> Dict[str, Any]:
    """Carga variables de entorno y define rutas estáticas y modelos para la arquitectura RAG.

    Returns:
        Diccionario con toda la configuración del proyecto.
    """
    root_dir = Path(__file__).resolve().parent.parent

    env_path = root_dir / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()

    data_raw_dir = root_dir / "data" / "raw"
    storage_dir = root_dir / "data" / "storage"

    data_raw_dir.mkdir(parents=True, exist_ok=True)
    storage_dir.mkdir(parents=True, exist_ok=True)

    gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    return {
        "root_dir": root_dir,
        "data_raw_dir": data_raw_dir,
        "storage_dir": storage_dir,
        "gemini_api_key": gemini_api_key,
        "llm_model": "gemini-3.1-flash-lite",
        "embed_model": "gemini-embedding-001",
        "embedding_dimension": DEFAULT_EMBEDDING_DIMENSION,
        "chunk_size": DEFAULT_CHUNK_SIZE,
        "chunk_overlap": DEFAULT_CHUNK_OVERLAP,
        "similarity_top_k": DEFAULT_SIMILARITY_TOP_K,
        "supported_extensions": SUPPORTED_EXTENSIONS,
        "hash_file_name": HASH_FILE_NAME,
        "cache_ttl_seconds": CACHE_TTL_SECONDS,
        "throttle_min_interval": THROTTLE_MIN_INTERVAL,
    }
