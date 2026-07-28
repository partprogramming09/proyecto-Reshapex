import os
import time
import json
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

DOC_HASHES_FILE = "doc_hashes.json"


class ThrottledGoogleGenAIEmbedding(GoogleGenAIEmbedding):
    """Modelo de embeddings con retardo de 2.0s y reintentos automáticos para evitar cuotas 429 de Gemini API."""

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        time.sleep(2.0)
        for attempt in range(4):
            try:
                return super()._get_text_embeddings(texts)
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    wait_time = 10 * (attempt + 1)
                    print(f"[RAG Embeddings] Cuota (429) alcanzada. Esperando {wait_time}s antes de reintentar (Intento {attempt + 1}/4)...")
                    time.sleep(wait_time)
                else:
                    raise e
        return super()._get_text_embeddings(texts)


def _get_embed_model() -> GoogleGenAIEmbedding:
    """Obtiene el modelo de embeddings de Google Gemini con throttling de tasa de peticiones.

    Returns:
        Instancia de ThrottledGoogleGenAIEmbedding configurada.

    Raises:
        ValueError: Si GEMINI_API_KEY no está configurada.
    """
    settings = get_settings()
    api_key = settings["gemini_api_key"]
    model_name = settings["embed_model"]
    if not api_key:
        raise ValueError("GEMINI_API_KEY no configurada para embeddings")
    return ThrottledGoogleGenAIEmbedding(
        model_name=model_name,
        api_key=api_key,
        embed_batch_size=5,
    )


def _get_file_hash(file_path: Path) -> str:
    """Calcula el hash MD5 del contenido binario de un archivo."""
    return hashlib.md5(file_path.read_bytes()).hexdigest()


def _load_doc_hashes(storage_dir: Path) -> Dict[str, str]:
    """Carga el mapa de hashes de documentos persistidos."""
    doc_hashes_path = storage_dir / DOC_HASHES_FILE
    if doc_hashes_path.exists():
        try:
            return json.loads(doc_hashes_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_doc_hashes(storage_dir: Path, hashes: Dict[str, str]) -> None:
    """Guarda el mapa de hashes de documentos persistidos."""
    doc_hashes_path = storage_dir / DOC_HASHES_FILE
    doc_hashes_path.write_text(json.dumps(hashes, indent=2, ensure_ascii=False), encoding="utf-8")


def _calculate_files_hash(directory: Path) -> str:
    """Calcula hash MD5 solo de los archivos con extensiones soportadas en un directorio.

    Args:
        directory: Directorio a escanear.

    Returns:
        Hash MD5 como string hexadecimal.
    """
    files = sorted(
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    content = "".join(f"{f.name}:{f.stat().st_size}" for f in files)
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
    """Carga índice persistido o realiza vectorización incremental idempotente por archivo.

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

    embed_model = _get_embed_model()
    doc_hashes = _load_doc_hashes(storage_dir)
    hash_file_path = storage_dir / HASH_FILE_NAME
    current_global_hash = _calculate_files_hash(data_raw_dir)

    index: Optional[VectorStoreIndex] = None

    # Intentar cargar índice existente desde disco
    storage_has_files = any(
        f for f in storage_dir.iterdir()
        if f.is_file() and not f.name.startswith(".") and f.name != DOC_HASHES_FILE
    )

    if storage_has_files:
        try:
            storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
            index = load_index_from_storage(storage_context, embed_model=embed_model)
        except Exception as e:
            print(f"[RAG] Error cargando índice existente: {e}. Se recreará el almacenamiento.")
            invalidate_index()
            index = None

    splitter = SentenceSplitter(
        chunk_size=settings["chunk_size"],
        chunk_overlap=settings["chunk_overlap"],
    )

    newly_indexed_count = 0

    # Ingestión Incremental e Idempotente por archivo
    for file_path in raw_documents:
        file_name = file_path.name
        current_file_hash = _get_file_hash(file_path)

        # Si el archivo ya fue vectorizado previamente, Omitir (Skip)
        if index is not None and doc_hashes.get(file_name) == current_file_hash:
            print(f"[RAG Idempotente] Skip (Ya vectorizado): {file_name}")
            continue

        print(f"[RAG Idempotente] Indexando nuevo/modificado: {file_name}...")
        try:
            doc_reader = SimpleDirectoryReader(input_files=[str(file_path)]).load_data()
            nodes = splitter.get_nodes_from_documents(doc_reader)

            if index is None:
                index = VectorStoreIndex(nodes, embed_model=embed_model)
            else:
                index.insert_nodes(nodes)

            doc_hashes[file_name] = current_file_hash
            newly_indexed_count += 1

            # Persistir inmediatamente tras procesar cada documento
            index.storage_context.persist(persist_dir=str(storage_dir))
            _save_doc_hashes(storage_dir, doc_hashes)
            print(f"[RAG Idempotente] Guardado en storage: {file_name} ({len(nodes)} fragmentos)")

        except Exception as e:
            print(f"[RAG Idempotente] Error al indexar {file_name}: {e}")

    if index is not None:
        hash_file_path.write_text(current_global_hash)
        if newly_indexed_count > 0:
            print(f"[RAG Idempotente] Ingestión completada. {newly_indexed_count} documento(s) nuevos indexados.")
        else:
            print(f"[RAG Idempotente] Todos los {len(raw_documents)} documentos ya estaban al día en caché.")

    return index
