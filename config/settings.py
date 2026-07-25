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

    openai_api_key = os.getenv("OPENAI_API_KEY", "")

    return {
        "root_dir": root_dir,
        "data_raw_dir": data_raw_dir,
        "storage_dir": storage_dir,
        "openai_api_key": openai_api_key,
        "llm_model": "gpt-4o-mini",
        "embed_model": "text-embedding-3-small",
    }
