import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from src.rag.indexer import load_or_create_index
from llama_index.core.tools import QueryEngineTool, ToolMetadata


def get_lls_knowledge_tool() -> QueryEngineTool:
    """Instancia y retorna la herramienta RAG QueryEngineTool para buscar en la base de conocimiento LLS Electric."""
    index = load_or_create_index()
    query_engine = index.as_query_engine(similarity_top_k=3)

    return QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="base_conocimiento_lls",
            description=(
                "Utilizar esta herramienta para consultar manuales técnicos, "
                "códigos de error (OCT, OVT, ETH, NTC), causas probables, soluciones "
                "y catálogos de equivalencias de equipos de automatización LLS Electric / LS Electric."
            ),
        ),
    )
