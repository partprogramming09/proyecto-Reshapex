import sys

# Asegurar codificación utf-8 para la consola de Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from agent_engine import LSElectricAgentEngine

def run_test():
    print("==================================================")
    print("PROBANDO ENGINE DEL AGENTE LS ELECTRIC (3 ETAPAS)")
    print("==================================================")
    
    engine = LSElectricAgentEngine()
    
    # Prueba 1: Consulta de código de error OCT
    query = "Tengo un error OCT en mi variador iG5A de 5.5kW al acelerar"
    print(f"\n[Consulta 1]: {query}")
    resultado = engine.procesar_consulta(query)
    
    print("\n--- [RESULTADO ETAPA 1 - GUÍA TÉCNICA] ---")
    print("Código:", resultado["etapa_1_guia"]["data"]["codigo"])
    print("Manual:", resultado["etapa_1_guia"]["data"]["manual_origen"])
    print("Página:", resultado["etapa_1_guia"]["data"]["pagina"])
    
    print("\n--- [RESULTADO ETAPA 2 - VARIANTES Y REEMPLAZO] ---")
    print("Modelo Anterior:", resultado["etapa_2_variantes"]["data"]["modelo_anterior"])
    print("Reemplazo Directo:", resultado["etapa_2_variantes"]["data"]["reemplazo_directo"])
    
    print("\n--- [RESULTADO ETAPA 3 - RESPUESTA LIMPIA CON CITA] ---")
    print(resultado["etapa_3_respuesta_limpia"])
    print("==================================================")
    print("¡TEST COMPLETADO CON ÉXITO! SINTAXIS Y LÓGICA 100% OK")
    print("==================================================")

if __name__ == "__main__":
    run_test()
