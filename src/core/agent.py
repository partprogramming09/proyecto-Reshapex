import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from config.settings import get_settings
from src.tools.rag_tools import get_lls_knowledge_tool
from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding


def build_agent() -> ReActAgent:
    """Construye e inicializa el ReActAgent para LLS Electric configurando el LLM y la herramienta RAG."""
    settings = get_settings()

    # Inicializar LLM y Embeddings usando la configuración
    llm = OpenAI(
        model=settings["llm_model"],
        api_key=settings["openai_api_key"],
        temperature=0.1,
    )
    embed_model = OpenAIEmbedding(
        model_name=settings["embed_model"],
        api_key=settings["openai_api_key"],
    )

    # Asignar a Settings de LlamaIndex de forma segura dentro del scope de la función
    Settings.llm = llm
    Settings.embed_model = embed_model

    # Obtener herramienta de conocimiento RAG
    knowledge_tool = get_lls_knowledge_tool()

    # Instanciar y retornar el ReActAgent
    agent = ReActAgent.from_tools(
        tools=[knowledge_tool],
        llm=llm,
        verbose=True,
    )

    return agent
