import os
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv


@lru_cache(maxsize=1)
def get_settings() -> dict:
    """Carga variables de entorno y define rutas estáticas y modelos para la arquitectura RAG."""
    # Obtener el directorio raíz del proyecto (dos niveles arriba de config/settings.py)
    root_dir = Path(__file__).resolve().parent.parent

    # Cargar .env desde el directorio raíz
    env_path = root_dir / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()

    # Definición de rutas dinámicas usando pathlib
    data_raw_dir = root_dir / "data" / "raw"
    storage_dir = root_dir / "data" / "storage"

    # Creación segura de directorios de almacenamiento si no existen
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
        "chunk_size": 1024,
        "chunk_overlap": 20,
        "similarity_top_k": 4,
    }
