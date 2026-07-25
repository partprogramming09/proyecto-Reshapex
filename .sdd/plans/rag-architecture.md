# Plan Técnico: Arquitectura RAG Modular para LS Electric

## Análisis Arquitectónico
La arquitectura adopta el patrón Modular Backend + Agente ReAct con LlamaIndex 0.10+.
Se elimina todo uso de variables globales globales mutables a favor de funciones puras, inyección de dependencias y decoradores de caché (`@lru_cache` para configuración y `@st.cache_resource` para el agente en Streamlit).

```
proyecto-Reshapex/
├── config/
│   └── settings.py          # Carga de .env y rutas pathlib con @lru_cache
├── data/
│   ├── raw/                 # Documentos de entrada (.txt, .pdf)
│   └── storage/             # Almacenamiento persistido del VectorStoreIndex
├── src/
│   ├── core/
│   │   └── agent.py         # Instanciación del ReActAgent
│   ├── rag/
│   │   └── indexer.py       # Lógica load_or_create_index
│   └── tools/
│       └── rag_tools.py     # Definición de QueryEngineTool para LlamaIndex
├── .env                     # Variables de entorno (OPENAI_API_KEY)
├── requirements.txt         # Dependencias del proyecto
└── app.py                   # Interfaz de usuario con Streamlit
```

## Archivos por Modificar/Crear
- `config/settings.py` (crear)
- `data/raw/manual_ls_electric.txt` (crear datos base)
- `src/rag/indexer.py` (crear)
- `src/tools/rag_tools.py` (crear)
- `src/core/agent.py` (crear)
- `requirements.txt` (actualizar)
- `.env` (crear plantilla)
- `app.py` (reescribir)

## Riesgos y Mitigaciones
* **Riesgo:** Recreación del índice vectorial en cada petición consume cuota y tiempo.
  * **Mitigación:** Persistencia en `data/storage/` + verificación previa de directorio no vacío.
* **Riesgo:** Reinicialización del agente por cada click en Streamlit.
  * **Mitigación:** Uso estricto de `@st.cache_resource` en la inicialización del agente.
