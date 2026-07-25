import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from src.core.agent import build_agent


def run_test():
    print("==================================================")
    print("PROBANDO AGENTE RAG LS ELECTRIC")
    print("==================================================")

    agent = build_agent()

    query = "Tengo un error OCT en mi variador iG5A de 5.5kW al acelerar"
    print(f"\n[Consulta]: {query}")
    print("\n--- [PROCESANDO] ---")
    respuesta = agent.chat(query)

    print("\n--- [RESULTADO] ---")
    print(respuesta)
    print("==================================================")
    print("¡TEST COMPLETADO!")
    print("==================================================")


if __name__ == "__main__":
    run_test()
