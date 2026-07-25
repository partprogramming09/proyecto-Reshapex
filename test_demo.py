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

    query1 = "Tengo un error OCT en mi variador iG5A de 5.5kW al acelerar"
    print(f"\n[Consulta 1]: {query1}")
    print("\n--- [PROCESANDO TURNO 1] ---")
    response1 = agent.chat(query1)
    print("\n--- [RESULTADO 1] ---")
    print(response1)

    query2 = "¿Cuál era el modelo de sustitución que me recomendaste en la respuesta anterior?"
    print(f"\n[Consulta 2 (Con Memoria)]: {query2}")
    print("\n--- [PROCESANDO TURNO 2] ---")
    response2 = agent.chat(query2)
    print("\n--- [RESULTADO 2] ---")
    print(response2)
    print("==================================================")
    print("¡TEST DE MEMORIA COMPLETADO!")
    print("==================================================")


if __name__ == "__main__":
    run_test()
