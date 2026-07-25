import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from src.core.agent_factory import AgentFactory


def run_test():
    """Ejecuta prueba del agente RAG LS Electric."""
    print("==================================================")
    print("PROBANDO AGENTE RAG LS ELECTRIC")
    print("==================================================")

    agent = AgentFactory.build_agent()

    query = "Tengo un error OCT en mi variador iG5A de 5.5kW al acelerar"
    print(f"\n[Consulta]: {query}")
    print("\n--- [PROCESANDO] ---")
    response = agent.chat(query)

    print("\n--- [RESULTADO] ---")
    print(response)
    print("==================================================")
    print("¡TEST COMPLETADO!")
    print("==================================================")


if __name__ == "__main__":
    run_test()
