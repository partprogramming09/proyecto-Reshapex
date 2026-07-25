import sys
from pathlib import Path

# Inyectar la raíz del proyecto al sys.path para importaciones relativas/absolutas limpias
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from config.settings import get_settings
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)


def load_or_create_index() -> VectorStoreIndex:
    """Carga un índice vectorial persistido en disco o genera uno nuevo a partir de data/raw/."""
    settings = get_settings()
    data_raw_dir = settings["data_raw_dir"]
    storage_dir = settings["storage_dir"]

    # Verificación si el directorio de almacenamiento está vacío
    storage_has_files = any(storage_dir.iterdir()) if storage_dir.exists() else False

    if not storage_has_files:
        # Si está vacío: leer datos crudos, crear el índice y persistirlo
        documents = SimpleDirectoryReader(input_dir=str(data_raw_dir)).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=str(storage_dir))
        return index
    else:
        # Si no está vacío: cargar el índice existente desde el almacenamiento en disco
        storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
        index = load_index_from_storage(storage_context)
        return index
