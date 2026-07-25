from typing import Optional
import subprocess
import urllib.request
import urllib.parse

from config.settings import get_settings
from src.rag.indexer import load_or_create_index, has_documents
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool


def get_knowledge_tool() -> Optional[QueryEngineTool]:
    """Herramienta PRIORIDAD: Consulta base de conocimiento local de LS Electric.

    Returns:
        QueryEngineTool si hay documentos disponibles, None de lo contrario.
    """
    if not has_documents():
        return None

    settings = get_settings()
    index = load_or_create_index()
    if index is None:
        return None

    query_engine = index.as_query_engine(
        similarity_top_k=settings["similarity_top_k"]
    )

    return QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="base_conocimiento_lls",
            description=(
                "PRIORIDAD: Consultar manuales técnicos LOCALES de LS Electric. "
                "Códigos de error (OCT, OVT, ETH, NTC), causas, soluciones, "
                "catálogos de migración iG5A a S100/H100, especificaciones técnicas. "
                "SIEMPRE usar esta herramienta PRIMERO antes de buscar en internet."
            ),
        ),
    )


def search_ls_electric_website(query: str) -> str:
    """Busca información en la página oficial de LS Electric.

    SOLO usar cuando base_conocimiento_lls no tenga la respuesta.

    Args:
        query: Consulta de búsqueda.

    Returns:
        Resultado de búsqueda con advertencia de que es información web no verificada.
    """
    try:
        search_query = f"site:lslcon.com OR site:lselectric.com {query}"
        url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}&num=3"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

        with urllib.request.urlopen(req, timeout=10) as response:
            print("Búsqueda web completada. Información de lslcon.com.")

        web_result = (
            f"🌐 [Fuente web - verificar con fuente oficial] "
            f"Búsqueda realizada para: {query}. "
            f"Consultar directamente lslcon.com para información verificada."
        )
        return web_result

    except Exception as e:
        return (
            f"🌐 [Búsqueda web no disponible] "
            f"No se pudo realizar la búsqueda para: {query}. "
            f"Error: {str(e)}. "
            f"Consultar directamente lslcon.com."
        )


def get_web_search_tool() -> FunctionTool:
    """Herramienta COMPLEMENTO: Búsqueda web oficial LS Electric.

    Returns:
        FunctionTool configurado para búsqueda web.
    """
    return FunctionTool.from_defaults(
        fn=search_ls_electric_website,
        name="busqueda_web_ls",
        description=(
            "COMPLEMENTO: Buscar información oficial de LS Electric en internet. "
            "SOLO usar cuando base_conocimiento_lls no tenga la respuesta. "
            "Siempre incluir advertencia de que es información web no verificada."
        ),
    )
