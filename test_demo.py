import sys

# Asegurar codificación utf-8 para la consola de Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from agent_engine import LSElectricAgentEngine

def run_test():
    print("==================================================")
    print("PROBANDO ENGINE DEL AGENTE LS ELECTRIC")
    print("==================================================")
    
    engine = LSElectricAgentEngine()
    
    query = "Tengo un error OCT en mi variador iG5A de 5.5kW al acelerar"
    print(f"\n[Consulta]: {query}")
    resultado = engine.procesar_consulta(query)
    
    print("\n--- [RESULTADO] ---")
    print(resultado["etapa_3_respuesta_limpia"])
    print("==================================================")
    print("¡TEST COMPLETADO!")
    print("==================================================")

if __name__ == "__main__":
    run_test()
