import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional, List, Dict

from config.settings import get_settings, SUPPORTED_EXTENSIONS, HASH_FILE_NAME
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding


def _get_embed_model() -> GoogleGenAIEmbedding:
    """Obtiene el modelo de embeddings de Google Gemini.

    Returns:
        Instancia de GoogleGenAIEmbedding configurada.

    Raises:
        ValueError: Si GEMINI_API_KEY no está configurada.
    """
    settings = get_settings()
    api_key = settings["gemini_api_key"]
    model_name = settings["embed_model"]
    if not api_key:
        raise ValueError("GEMINI_API_KEY no configurada para embeddings")
    return GoogleGenAIEmbedding(model_name=model_name, api_key=api_key)


def _calculate_files_hash(directory: Path) -> str:
    """Calcula hash MD5 de los archivos en un directorio.

    Args:
        directory: Directorio a escanear.

    Returns:
        Hash MD5 como string hexadecimal.
    """
    files = sorted(directory.glob("*"))
    content = "".join(f"{f.name}:{f.stat().st_size}" for f in files if f.is_file())
    return hashlib.md5(content.encode()).hexdigest()


def list_documents() -> List[Dict[str, str]]:
    """Lista documentos disponibles en data/raw/.

    Returns:
        Lista de diccionarios con nombre, tamaño y ruta de cada documento.
    """
    settings = get_settings()
    data_raw_dir = settings["data_raw_dir"]
    documents = []
    for f in sorted(data_raw_dir.iterdir()):
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            file_size = f.stat().st_size
            if file_size > 1024 * 1024:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            elif file_size > 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size} B"
            documents.append({"nombre": f.name, "tamaño": size_str, "path": str(f)})
    return documents


def count_pages() -> int:
    """Cuenta el número de páginas/fragmentos en el índice persistido.

    Returns:
        Número de páginas/fragmentos, o 0 si hay error.
    """
    settings = get_settings()
    storage_dir = settings["storage_dir"]
    try:
        from llama_index.core.storage.docstore import SimpleDocumentStore
        docstore = SimpleDocumentStore.from_persist_dir(persist_dir=str(storage_dir))
        return len(docstore.docs)
    except Exception:
        return 0


def invalidate_index() -> None:
    """Invalida el índice eliminando el directorio de storage."""
    settings = get_settings()
    storage_dir = settings["storage_dir"]
    if storage_dir.exists():
        shutil.rmtree(storage_dir)
        storage_dir.mkdir(parents=True, exist_ok=True)


def has_documents() -> bool:
    """Verifica si hay documentos disponibles en data/raw/.

    Returns:
        True si hay al menos un documento soportado, False de lo contrario.
    """
    settings = get_settings()
    data_raw_dir = settings["data_raw_dir"]
    if not data_raw_dir.exists():
        return False
    return any(
        f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        for f in data_raw_dir.iterdir()
    )


def load_or_create_index() -> Optional[VectorStoreIndex]:
    """Carga índice persistido o crea uno nuevo desde data/raw/.

    Returns:
        VectorStoreIndex si hay documentos, None si no hay documentos.
    """
    settings = get_settings()
    data_raw_dir = settings["data_raw_dir"]
    storage_dir = settings["storage_dir"]

    Settings.chunk_size = settings["chunk_size"]
    Settings.chunk_overlap = settings["chunk_overlap"]

    data_raw_dir.mkdir(parents=True, exist_ok=True)
    storage_dir.mkdir(parents=True, exist_ok=True)

    raw_documents = [
        f for f in data_raw_dir.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not raw_documents:
        print("[RAG] No hay documentos en data/raw/. Modo autónomo (solo Gemini).")
        return None

    current_hash = _calculate_files_hash(data_raw_dir)
    hash_file_path = storage_dir / HASH_FILE_NAME

    stored_hash = ""
    if hash_file_path.exists():
        stored_hash = hash_file_path.read_text().strip()

    storage_has_files = any(
        f for f in storage_dir.iterdir()
        if f.is_file() and not f.name.startswith(".")
    )

    if storage_has_files and current_hash == stored_hash:
        print("[RAG] Cargando índice persistido...")
        try:
            embed_model = _get_embed_model()
            storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
            index = load_index_from_storage(storage_context, embed_model=embed_model)
            print(f"[RAG] Índice cargado: {len(raw_documents)} documentos")
            return index
        except Exception as e:
            print(f"[RAG] Error cargando índice, regenerando: {e}")
            invalidate_index()

    print(f"[RAG] Indexando {len(raw_documents)} documentos...")
    try:
        embed_model = _get_embed_model()
        documents = SimpleDirectoryReader(
            input_dir=str(data_raw_dir),
            required_exts=SUPPORTED_EXTENSIONS,
        ).load_data()

        document_count = len(documents)
        print(f"[RAG] {document_count} páginas/fragmentos extraídos")

        splitter = SentenceSplitter(
            chunk_size=settings["chunk_size"],
            chunk_overlap=settings["chunk_overlap"],
        )
        index = VectorStoreIndex.from_documents(
            documents,
            embed_model=embed_model,
            transformations=[splitter],
        )
        index.storage_context.persist(persist_dir=str(storage_dir))

        hash_file_path.write_text(current_hash)
        print(f"[RAG] Índice persistido correctamente")
        return index

    except Exception as e:
        print(f"[RAG] Error al indexar: {e}")
        return None
