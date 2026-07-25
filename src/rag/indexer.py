import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from config.settings import get_settings
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.core.node_parser import SentenceSplitter


def load_or_create_index() -> VectorStoreIndex:
    """Carga un índice vectorial o crea uno nuevo desde data/raw/ con chunking 1024 tokens."""
    settings = get_settings()
    data_raw_dir = settings["data_raw_dir"]
    storage_dir = settings["storage_dir"]

    Settings.chunk_size = settings["chunk_size"]
    Settings.chunk_overlap = settings["chunk_overlap"]

    if settings["gemini_api_key"] and not settings["gemini_api_key"].startswith("tu_"):
        try:
            from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
            Settings.embed_model = GoogleGenAIEmbedding(
                model_name=settings["embed_model"],
                api_key=settings["gemini_api_key"],
            )
        except Exception as e:
            print(f"[Info] No se pudo configurar embed model de Google: {e}")

    storage_has_files = any(storage_dir.iterdir()) if storage_dir.exists() else False

    if not storage_has_files:
        documents = SimpleDirectoryReader(input_dir=str(data_raw_dir)).load_data()
        splitter = SentenceSplitter(
            chunk_size=settings["chunk_size"],
            chunk_overlap=settings["chunk_overlap"],
        )
        index = VectorStoreIndex.from_documents(
            documents,
            transformations=[splitter],
        )
        index.storage_context.persist(persist_dir=str(storage_dir))
        return index
    else:
        storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
        index = load_index_from_storage(storage_context)
        return index
