# Engine Context & Documentation — LS Electric AI Agent

Documentación completa del contexto, arquitectura, regla de negocio, pipeline RAG idempotente, gestión de memoria y stack técnico final para la Hackaton **AgentSprint (ReshapeX)**.

---

## 1. Información General de la Hackaton

* **Evento:** AgentSprint — AI Hackathon por ReshapeX.
* **Lugar / Fecha:** Universidad EAFIT, Medellín · 8:00 AM – 12:00 PM.
* **Formato:** ~3.5 horas de desarrollo continuo en equipos de 3 a 4 integrantes.
* **Empresa / Marca Seleccionada:** **LS Electric** (Líder en Automatización Industrial y Control de Potencia).
* **Premios:** $2.000.000 COP | $1.000.000 COP | $500.000 COP.

### Criterios de Evaluación (100% Total):
1. **Progreso / Hitos (30%):** De Setup inicial a Respuestas Fundamentadas (Grounded) con herramientas/manuales.
2. **Innovación (30%):** Originalidad y utilidad real para la industria OEM.
3. **Checklist Técnico (20%):** Funcionamiento real de los componentes (Tools, RAG, Loop, Guardrails) en código.
4. **Calidad de Código y Git (10%):** Repositorio limpio, sin claves expuestas (`.env`), commits ordenados.
5. **Pitch & Presentación (10%):** Demo en vivo de 2 minutos limpia y respuesta a jurados.

---

## 2. Contexto de Negocio: LS Electric (OEM)

**LS Electric** fabrica equipos de automatización de alta gama:
* **Variadores de Frecuencia (VFD / Inverters):** Series iG5A (descontinuado/obsoleto popular), S100 (Estándar), H100 (HVAC/Bombas), M100 (Micro).
* **PLCs y HMIs:** Serie XGB, XGK e iXP2.

### El Problema de Negocio Solucionado:
Los ingenieros y técnicos de planta se enfrentan a:
1. Paradas de planta por códigos de falla en variadores (ej. `OCT`, `OVT`, `ETH`, `NTC`).
2. Necesidad urgente de sustituir variadores viejos (iG5A) por series actuales (S100/H100) manteniendo potencia, voltaje y dimensiones.

---

## 3. Regla de Negocio Constante (Flujo en 3 Etapas)

El agente opera bajo una arquitectura de 3 etapas secuenciales y obligatorias:

```
+-------------------------------------------------------------------+
|                     ETAPA 1: GUÍA TÉCNICA                          |
| Consultar Manuales y BBDD de Fallas (OCT, OVT, ETH, NTC)          |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                ETAPA 2: VARIANTES Y SUSTITUTOS                    |
| Evaluar Matriz de Migración (ej. iG5A 5.5kW -> S100-4 5.5kW)      |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|             ETAPA 3: RESPUESTA GROUNDED CON CITA REAL             |
| Cita obligatoria con archivo PDF y número de página física        |
+-------------------------------------------------------------------+
```

### Detalle de las Etapas:
1. **Etapa 1 (Consulta de Guía):** Identifica el código de error, la causa raíz exacta y las acciones correctivas paso a paso.
2. **Etapa 2 (Revisión de Variantes):** Mapea el modelo consultado contra el catálogo de sustitución directa/premium y especifica compatibilidad de montaje.
3. **Etapa 3 (Cita de Origen Verídica):** Genera la respuesta citando **obligatoriamente el archivo PDF real y la página física** (`📑 Fuente: Manual [nombre.pdf], Página [X]`) o la URL web oficial (`🌐 Fuente Web Oficial: [URL]`). Está prohibido emitir citas genéricas o de plantilla.

---

## 4. Tech Stack Final

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Runtime | Python | >= 3.10 |
| UI/Web | Streamlit | >= 1.32.0 |
| Framework RAG | LlamaIndex Core | >= 0.14.0 |
| LLM Provider | Google Gemini (google-genai SDK) | >= 2.0.0 |
| LLM Adapter | llama-index-llms-google-genai | >= 0.9.0 |
| Embeddings | llama-index-embeddings-google-genai | >= 0.5.0 |
| File Readers | llama-index-readers-file | >= 0.6.0 |
| Env Vars | python-dotenv | >= 1.0.0 |
| Modelo LLM Principal | gemini-3.1-flash-lite | (en `config/settings.py`) |
| Modelos Fallback | gemini-3.5-flash-lite, gemma-4-26b-a4b-it | (en `src/core/engine.py`) |
| Modelo Embeddings | gemini-embedding-001 | (en `config/settings.py`) |

---

## 5. Arquitectura del Proyecto y Componentes Avanzados

```
                    +-----------------------------------------+
                    |       UI: Streamlit (app.py)            |
                    |   Theme Industrial + Chat Decomposed    |
                    +------------------+----------------------+
                                       |
                    +------------------v----------------------+
                    |    AgentFactory.build_agent()           |
                    |  (factory pattern, fallback)            |
                    +--------+------------------+-------------+
                             |                  |
               +-------------v---+    +---------v--------------+
               |   ReActAgent    |    | FallbackAgentWrapper   |
               |  + AgentMemory  |    | (google-genai directo) |
               |   con 2 tools   |    +------------------------+
               +--+-----------+--+
                  |           |
      +-----------v--+  +----v------------------+
      | base_        |  | busqueda_             |
      | conocimiento |  | web_ls                |
      | _lls         |  | (Google Search API)   |
      | (RAG query)  |  +-----------------------+
      +------+-------+
             |
   +---------v------------------------+
   |   VectorStoreIndex               |
   |   Ingestión Idempotente por Hash |
   |   Throttled Embeddings (2s)      |
   |   data/storage/ (persist)        |
   +---------------------------------+
```

### Patrón Factory & Memory Manager
* `AgentFactory`: Construye el agente singleton.
* `AgentMemoryManager` (`src/core/memory.py`): Envuelve `ChatMemoryBuffer` (límite de 3000 tokens) e integra memoria conversacional mutiturno tanto en `ReActAgentWrapper` como en `FallbackAgentWrapper`.

### Ingestión RAG Idempotente por Hash (`src/rag/indexer.py`)
* **Content-Based Hashing:** Registra el hash MD5 de cada PDF en `data/storage/doc_hashes.json`. Si un documento ya fue procesado, se omite su vectorización ($O(1)$ Skip), ahorrando el 100% de la cuota diaria de API de embeddings.
* **Throttling & Exponential Backoff:** `ThrottledGoogleGenAIEmbedding` aplica retardo automático de 2.0s entre lotes y reintentos exponenciales ante errores `429 RESOURCE_EXHAUSTED`.
* **Persistencia Integrada:** Guarda `docstore.json`, `index_store.json`, `default__vector_store.json`, `doc_hashes.json` y `.hash` en `data/storage/`.

### Extracción de Metadatos y Citas Verídicas (`src/tools/rag_tools.py`)
* `QueryEngineTool` inyecta directamente `LLMFactory.get_llm()` y extrae los metadatos de los nodos devueltos (`file_name` y `page_label`), eliminando alucinaciones y garantizando citas de archivo y página física exactos.

---

## 6. Estructura de Archivos del Proyecto

```
proyecto Reshapex/
├── app.py                          # Entry point UI Streamlit principal
├── test_demo.py                    # Test de integración y flujo de memoria
├── requirements.txt                # Dependencias (7 paquetes principales)
├── readme.md                       # Documentación hackathon
├── AGENTS.md                       # Especificación técnica y contexto final
├── PITCH_DEMO_2MIN.md              # Guion de Pitch de 2 minutos y preguntas de jurados
├── .env                            # Variables de entorno (NO versionado)
├── .env.example                    # Plantilla de env
├── .gitignore                      # Excluye .env, __pycache__, data/storage/
│
├── .streamlit/
│   └── config.toml                 # Tema visual Streamlit (dark mode, #FFD700)
│
├── config/
│   ├── __init__.py                 # Exporta get_settings
│   ├── settings.py                 # Config central: rutas, modelos, constantes
│   └── llm_factory.py              # Factory para LLM y embeddings Gemini
│
├── src/
│   ├── core/
│   │   ├── __init__.py             # Exporta wrappers, factory, prompts, engine y memory
│   │   ├── agent.py                # FallbackAgentWrapper con RAG y AgentMemoryManager
│   │   ├── agent_factory.py        # AgentFactory: ReActAgentWrapper con memoria
│   │   ├── engine.py               # LSElectricAgentEngine con prompt estricto y caché MD5
│   │   ├── memory.py               # AgentMemoryManager (ChatMemoryBuffer)
│   │   └── prompts.py              # SYSTEM_PROMPT_AGENT para ReActAgent
│   │
│   ├── rag/
│   │   ├── __init__.py             # Exporta funciones de indexación y verificación
│   │   └── indexer.py              # VectorStoreIndex con hash por archivo y Throttling
│   │
│   └── tools/
│       ├── __init__.py             # Exporta herramientas de conocimiento y web
│       └── rag_tools.py            # QueryEngineTool con LLMFactory y metadatos
│
├── ui/
│   ├── __init__.py                 # Exporta componentes UI
│   ├── chat.py                     # Renderizado del chat, 3 etapas y persistencia de input
│   ├── sidebar.py                  # Panel lateral de gestión de documentos sin borrado accidental
│   └── theme.py                    # Estilos CSS industriales y badges de estado
│
├── utils/
│   ├── __init__.py                 # Exporta funciones de parsing
│   └── response_parser.py          # Extractor robusto por posiciones de 3 etapas
│
└── data/
    ├── raw/                        # Documentos PDF de entrada (manuales LS Electric)
    └── storage/                    # Base vectorial persistida (7 archivos JSON / hash)
```

---

## 7. Variables de Entorno y Configuración

### Variables de Entorno (.env)

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `GEMINI_API_KEY` | SÍ | API Key de Google AI Studio para Gemini. |

### Constantes Configurables (config/settings.py)

| Constante | Valor | Descripción |
|-----------|-------|-------------|
| `SUPPORTED_EXTENSIONS` | `[".pdf", ".txt", ".md"]` | Extensiones de archivos indexables |
| `DEFAULT_CHUNK_SIZE` | `1024` | Tamaño de chunk para splitting |
| `DEFAULT_CHUNK_OVERLAP` | `20` | Overlap entre chunks |
| `DEFAULT_SIMILARITY_TOP_K` | `4` | Top-K para búsqueda vectorial |
| `CACHE_TTL_SECONDS` | `300` | TTL del caché de respuestas (5 min) |
| `MIN_QUERY_INTERVAL` | `3.0` | Intervalo mínimo entre consultas en la UI |

---

## 8. Guía de Instalación y Ejecución

### 1. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configuración de Entorno
Crear `.env` en la raíz del proyecto:
```env
GEMINI_API_KEY=tu_api_key_de_google_ai_studio
```

### 3. Ejecución de la Aplicación Web (Streamlit)
```bash
streamlit run app.py
```

### 4. Ejecución del Test de Integración
```bash
python test_demo.py
```

---

## 9. Flujo Ejecutivo del Agente

1. **Startup:** `app.py` ejecuta `apply_custom_theme()` e inicializa `AgentFactory.build_agent()` con `@st.cache_resource`.
2. **Ingestión Idempotente:** Si existen PDFs en `data/raw/`, `indexer.py` verifica `doc_hashes.json`. Omite archivos conocidos ($O(1)$ skip) e indexa únicamente documentos nuevos o modificados.
3. **Consulta Multiturno:** `ui/chat.py` recibe el prompt, mantiene la entrada `st.chat_input` siempre visible en el DOM, actualiza `AgentMemoryManager` e invoca al agente.
4. **Respuesta Desglosada:** `response_parser.py` parsea la salida en las 3 etapas (`diagnostico`, `variante`, `cita`) y las renderiza en 3 tarjetas expandibles.

---

## 10. Estrategia Git

* **Rama Principal:** `main` (Código estable ejecutable).
* **Ramas de Trabajo:** `Hernan-features`, `fredy-feature`, `junior-feature`.
