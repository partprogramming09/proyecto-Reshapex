import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from config.settings import get_settings
from src.rag.indexer import load_or_create_index, hay_documentos
from llama_index.core.tools import QueryEngineTool, ToolMetadata


def get_lls_knowledge_tool():
    """Herramienta RAG: Consulta base de conocimiento de LS Electric."""
    if not hay_documentos():
        return None

    index = load_or_create_index()
    if index is None:
        return None

    query_engine = index.as_query_engine(similarity_top_k=5)

    return QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="base_conocimiento_lls",
            description=(
                "Consultar manuales técnicos de LS Electric. "
                "Códigos de error (OCT, OVT, ETH, NTC), causas, soluciones, "
                "catálogos de migración iG5A a S100/H100, especificaciones técnicas."
            ),
        ),
    )
