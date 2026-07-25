import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional, List, Dict

from config.settings import get_settings
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding


def _get_embed_model():
    settings = get_settings()
    api_key = settings["gemini_api_key"]
    model_name = settings["embed_model"]
    if not api_key:
        raise ValueError("GEMINI_API_KEY no configurada para embeddings")
    return GoogleGenAIEmbedding(model_name=model_name, api_key=api_key)


def _hash_archivos(directorio: Path) -> str:
    archivos = sorted(directorio.glob("*"))
    contenido = "".join(f"{a.name}:{a.stat().st_size}" for a in archivos if a.is_file())
    return hashlib.md5(contenido.encode()).hexdigest()


def listar_documentos() -> List[Dict]:
    settings = get_settings()
    data_raw_dir = settings["data_raw_dir"]
    docs = []
    for f in sorted(data_raw_dir.iterdir()):
        if f.is_file() and f.suffix.lower() in (".pdf", ".txt", ".md"):
            tamaño = f.stat().st_size
            if tamaño > 1024 * 1024:
                tamaño_str = f"{tamaño / (1024 * 1024):.1f} MB"
            elif tamaño > 1024:
                tamaño_str = f"{tamaño / 1024:.1f} KB"
            else:
                tamaño_str = f"{tamaño} B"
            docs.append({"nombre": f.name, "tamaño": tamaño_str, "path": str(f)})
    return docs


def contar_paginas() -> int:
    settings = get_settings()
    storage_dir = settings["storage_dir"]
    try:
        from llama_index.core.storage.docstore import SimpleDocumentStore
        docstore = SimpleDocumentStore.from_persist_dir(persist_dir=str(storage_dir))
        return len(docstore.docs)
    except Exception:
        return 0


def invalidar_indice():
    settings = get_settings()
    storage_dir = settings["storage_dir"]
    if storage_dir.exists():
        shutil.rmtree(storage_dir)
        storage_dir.mkdir(parents=True, exist_ok=True)


def hay_documentos() -> bool:
    settings = get_settings()
    data_raw_dir = settings["data_raw_dir"]
    if not data_raw_dir.exists():
        return False
    return any(
        f.is_file() and f.suffix.lower() in (".pdf", ".txt", ".md")
        for f in data_raw_dir.iterdir()
    )


def load_or_create_index() -> Optional[VectorStoreIndex]:
    settings = get_settings()
    data_raw_dir = settings["data_raw_dir"]
    storage_dir = settings["storage_dir"]

    data_raw_dir.mkdir(parents=True, exist_ok=True)
    storage_dir.mkdir(parents=True, exist_ok=True)

    docs_en_raw = [
        f for f in data_raw_dir.iterdir()
        if f.is_file() and f.suffix.lower() in (".pdf", ".txt", ".md")
    ]

    if not docs_en_raw:
        print("[RAG] No hay documentos en data/raw/. Modo autónomo (solo Gemini).")
        return None

    hash_actual = _hash_archivos(data_raw_dir)
    hash_file = storage_dir / ".hash"

    hash_storage = ""
    if hash_file.exists():
        hash_storage = hash_file.read_text().strip()

    storage_has_files = any(
        f for f in storage_dir.iterdir()
        if f.is_file() and not f.name.startswith(".")
    )

    if storage_has_files and hash_actual == hash_storage:
        print("[RAG] Cargando índice persistido...")
        try:
            embed_model = _get_embed_model()
            storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
            index = load_index_from_storage(storage_context, embed_model=embed_model)
            print(f"[RAG] Índice cargado: {len(docs_en_raw)} documentos")
            return index
        except Exception as e:
            print(f"[RAG] Error cargando índice, regenerando: {e}")
            invalidar_indice()

    print(f"[RAG] Indexando {len(docs_en_raw)} documentos...")
    try:
        embed_model = _get_embed_model()
        documents = SimpleDirectoryReader(
            input_dir=str(data_raw_dir),
            required_exts=[".pdf", ".txt", ".md"],
        ).load_data()

        num_docs = len(documents)
        print(f"[RAG] {num_docs} páginas/fragmentos extraídos")

        index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
        index.storage_context.persist(persist_dir=str(storage_dir))

        hash_file.write_text(hash_actual)
        print(f"[RAG] Índice persistido correctamente")
        return index

    except Exception as e:
        print(f"[RAG] Error al indexar: {e}")
        return None
