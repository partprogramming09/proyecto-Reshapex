# Engine Context & Documentation — LS Electric AI Agent

Documentacion completa del contexto, arquitectura, regla de negocio y stack tecnico para la Hackaton **AgentSprint (ReshapeX)**.

---

## 1. Informacion General de la Hackaton

* **Evento:** AgentSprint — AI Hackathon por ReshapeX.
* **Lugar / Fecha:** Universidad EAFIT, Medellin · 8:00 AM – 12:00 PM.
* **Formato:** ~3.5 horas de desarrollo continuo en equipos de 3 a 4 integrantes.
* **Empresa / Marca Seleccionada:** **LS Electric** (Lider en Automatizacion Industrial y Control de Potencia).
* **Premios:** $2.000.000 COP | $1.000.000 COP | $500.000 COP.

### Criterios de Evaluacion (100% Total):
1. **Progreso / Hitos (30%):** De Setup inicial a Respuestas Fundamentadas (Grounded) con herramientas/manuales.
2. **Innovacion (30%):** Originalidad y utilidad real para la industria OEM.
3. **Checklist Tecnico (20%):** Funcionamiento real de los componentes (Tools, RAG, Loop, Guardrails) en codigo.
4. **Calidad de Codigo y Git (10%):** Repositorio limpio, sin claves expuestas (`.env`), commits ordenados.
5. **Pitch & Presentacion (10%):** Demo en vivo de 2 minutos limpia y respuesta a jurados.

---

## 2. Contexto de Negocio: LS Electric (OEM)

**LS Electric** fabrica equipos de automatizacion de alta gama:
* **Variadores de Frecuencia (VFD / Inverters):** Series iG5A (descontinuado/obsoleto popular), S100 (Estandar), H100 (HVAC/Bombas), M100 (Micro).
* **PLCs y HMIs:** Serie XGB, XGK e iXP2.

### El Problema de Negocio Solucionado:
Los ingenieros y tecnicos de planta se enfrentan a:
1. Paradas de planta por codigos de falla en variadores (ej. `OCT`, `OVT`, `ETH`, `NTC`).
2. Necesidad urgente de sustituir variadores viejos (iG5A) por series actuales (S100/H100) manteniendo potencia, voltaje y dimensiones.

---

## 3. Regla de Negocio Constante (Flujo en 3 Etapas)

El agente opera bajo una arquitectura de 3 etapas secuenciales y obligatorias:

```
+-------------------------------------------------------------------+
|                     ETAPA 1: GUIA TECNICA                          |
| Consultar Manuales y BBDD de Fallas (OCT, OVT, ETH, NTC)          |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                ETAPA 2: VARIANTES Y SUSTITUTOS                    |
| Evaluar Matriz de Migracion (ej. iG5A 5.5kW -> S100-4 5.5kW)     |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|             ETAPA 3: RESPUESTA GROUNDED CON CITA                  |
| Sintetizar respuesta en Markdown citando Manual, Seccion y Pag.   |
+-------------------------------------------------------------------+
```

### Detalle de las Etapas:
1. **Etapa 1 (Consulta de Guia):** Identifica el codigo de error, la causa raiz y la lista de acciones correctivas recomendadas.
2. **Etapa 2 (Revision de Variantes):** Mapea el modelo consultado contra el catalogo de sustitucion directa/premium y especifica compatibilidad de montaje.
3. **Etapa 3 (Cita de Origen):** Genera la respuesta en Markdown incluyendo obligatoriamente la cita formal (`Cita Oficial del Manual: Manual X, Seccion Y, Pag. Z`).

---

## 4. Tech Stack

| Capa | Tecnologia | Version |
|------|-----------|---------|
| Runtime | Python | >= 3.10 |
| UI/Web | Streamlit | >= 1.32.0 |
| Framework RAG | LlamaIndex Core | >= 0.14.0 |
| LLM Provider | Google Gemini (google-genai SDK) | >= 2.0.0 |
| LLM Adapter | llama-index-llms-google-genai | >= 0.9.0 |
| Embeddings | llama-index-embeddings-google-genai | >= 0.5.0 |
| File Readers | llama-index-readers-file | >= 0.6.0 |
| Env Vars | python-dotenv | >= 1.0.0 |
| Modelo LLM Principal | gemini-3.1-flash-lite | (en config/settings.py) |
| Modelos Fallback | gemini-3.5-flash-lite, gemma-4-26b-a4b-it | (en src/core/engine.py) |
| Modelo Embeddings | gemini-embedding-001 | (en config/settings.py) |

---

## 5. Arquitectura del Proyecto

```
                    +-----------------------------------------+
                    |       UI: Streamlit (app.py)            |
                    |   @st.cache_resource (agente)           |
                    +------------------+----------------------+
                                       |
                    +------------------v----------------------+
                    |    AgentFactory.build_agent()           |
                    |  (factory pattern, fallback)            |
                    +--------+------------------+-------------+
                             |                  |
               +-------------v---+    +---------v--------------+
               |   ReActAgent    |    | FallbackAgentWrapper   |
               |   (LlamaIndex)  |    | (google-genai directo) |
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
   |   VectorStoreIndex              |
   |   (LlamaIndex + Gemini         |
   |    embeddings)                  |
   |   data/storage/ (persist)       |
   +---------------------------------+
```

### Patron Factory
`AgentFactory` construye el agente: intenta crear `ReActAgent` con 2 tools. Si falla, retorna `FallbackAgentWrapper`.

### Patron Fallback (Chain of Responsibility)
Si `ReActAgent` no esta disponible o falla, `FallbackAgentWrapper` usa `google-genai` SDK directo con `LSElectricAgentEngine` como motor de respaldo.

### Pipeline RAG
`src/rag/indexer.py` indexa PDFs de `data/raw/` en un `VectorStoreIndex` con Gemini embeddings. Persiste en `data/storage/`. Usa hash-based invalidation para no re-indexar documentos sin cambios.

### Triple Cache
- `@lru_cache` en `config/settings.py` (config inmutable)
- `@st.cache_resource` en `app.py` (agente singleton)
- Cache dict en `engine.py` (respuestas, TTL 300s)

### Throttling
- Engine: `_throttle()` con 2s minimo entre requests
- UI: `MIN_QUERY_INTERVAL` de 3s

---

## 6. Estructura de Archivos

```
proyecto Reshapex/
├── app.py                          # Entry point - UI Streamlit (285 lineas)
├── test_demo.py                    # Test de integracion del agente (30 lineas)
├── requirements.txt                # Dependencias (7 paquetes)
├── readme.md                       # Documentacion hackathon
├── AGENTS.md                       # Este archivo: contexto del agente
├── .env                            # Variables de entorno (NO versionado)
├── .env.example                    # Plantilla de env (1 variable)
├── .gitignore                      # Ignorar .env, __pycache__, data/storage/
│
├── .streamlit/
│   └── config.toml                 # Tema visual Streamlit (dark mode)
│
├── .skills/
│   └── OEM-Agent-Workflow/
│       └── SKILL.md                # Skill opencode: workflow OEM 3 etapas
│
├── .sdd/                           # Spec-Driven Development docs
│   ├── specs/rag-architecture.md
│   ├── plans/rag-architecture.md
│   └── tasks/rag-architecture.md
│
├── config/
│   ├── __init__.py                 # Exporta get_settings
│   ├── settings.py                 # Config central: rutas, modelos, constantes
│   └── llm_factory.py              # Factory para LLM y embeddings Gemini
│
├── src/
│   ├── core/
│   │   ├── __init__.py             # Exporta: FallbackAgentWrapper, AgentFactory, prompts, engine
│   │   ├── agent.py                # FallbackAgentWrapper con RAG opcional
│   │   ├── agent_factory.py        # AgentFactory: construye ReActAgent o fallback
│   │   ├── engine.py               # LSElectricAgentEngine: motor principal 3 etapas
│   │   └── prompts.py              # SYSTEM_PROMPT_AGENT para ReActAgent
│   │
│   ├── rag/
│   │   ├── __init__.py             # Exporta: load_or_create_index, has_documents, etc.
│   │   └── indexer.py              # VectorStoreIndex con LlamaIndex + hash cache
│   │
│   └── tools/
│       ├── __init__.py             # Exporta: get_knowledge_tool, get_web_search_tool
│       └── rag_tools.py            # QueryEngineTool + FunctionTool web search
│
└── data/
    ├── raw/                        # Documentos PDF de entrada
    │   └── LS_ELECTRIC_*.pdf
    └── storage/                    # VectorStoreIndex persistido (.gitignored)
```

---

## 7. Variables de Entorno y Configuracion

### Variables de Entorno (.env)

| Variable | Requerida | Descripcion |
|----------|-----------|-------------|
| `GEMINI_API_KEY` | SI | API Key de Google AI Studio para Gemini. Sin ella, el agente usa solo modo autonomo con mensaje de error. |

### Constantes Configurables (config/settings.py)

| Constante | Valor | Descripcion |
|-----------|-------|-------------|
| `SUPPORTED_EXTENSIONS` | `[".pdf", ".txt", ".md"]` | Extensiones de archivos indexables |
| `DEFAULT_CHUNK_SIZE` | `1024` | Tamano de chunk para splitting |
| `DEFAULT_CHUNK_OVERLAP` | `20` | Overlap entre chunks |
| `DEFAULT_SIMILARITY_TOP_K` | `4` | Top-K para busqueda vectorial |
| `DEFAULT_EMBEDDING_DIMENSION` | `768` | Dimension de embeddings |
| `HASH_FILE_NAME` | `.hash` | Archivo de cache de hash |
| `CACHE_TTL_SECONDS` | `300` | TTL del cache de respuestas (5 min) |
| `THROTTLE_MIN_INTERVAL` | `2.0` | Intervalo minimo entre requests al LLM (segundos) |

### Rutas Fijas

| Ruta | Proposito |
|------|-----------|
| `data/raw/` | Documentos de entrada (PDFs manuales LS Electric) |
| `data/storage/` | VectorStoreIndex persistido (auto-creado) |
| `.streamlit/config.toml` | Tema visual (dark mode, color primario #FFD700) |

---

## 8. Guia de Instalacion y Ejecucion

### Requisitos Previos
Python 3.10 o superior.

### 1. Instalacion de Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configuracion de Variables de Entorno
Crear un archivo `.env` en la raiz del proyecto (opcional si se ingresa la clave desde la interfaz):
```env
GEMINI_API_KEY=tu_api_key_de_google_ai_studio
```

### 3. Ejecucion de la Aplicacion Web (Streamlit)
```bash
streamlit run app.py
```

### 4. Ejecucion del Test de Integracion
```bash
python test_demo.py
```

### Notas
- No hay herramientas de linting/formateo configuradas (sin ruff, mypy, black, etc.)
- No hay framework de testing (pytest, unittest). Solo `test_demo.py` como smoke test manual.

---

## 9. Flujo del Agente

1. **Startup:** `app.py` llama `AgentFactory.build_agent()` con `@st.cache_resource` (singleton por sesion).
2. **AgentFactory:** Intenta crear `ReActAgent` con 2 tools:
   - `base_conocimiento_lls`: Query RAG sobre PDFs indexados en VectorStoreIndex.
   - `busqueda_web_ls`: Busqueda web via Google Search API.
   Si falla, retorna `FallbackAgentWrapper`.
3. **Indexacion RAG:** Si hay PDFs en `data/raw/`, `indexer.py` carga o crea `VectorStoreIndex` con Gemini embeddings, lo persiste en `data/storage/`.
4. **Query del usuario:** El agente pasa por 3 etapas obligatorias (diagnostico, recomendacion, cita) definidas en `prompts.py`.
5. **Fallback engine:** `LSElectricAgentEngine` usa `google-genai` SDK directo con fallback entre 3 modelos y cache MD5 de respuestas.
6. **UI:** Streamlit parsea la respuesta en 3 expanders visuales.

---

## 10. Estrategia Git

* **Rama Principal:** `main` (Codigo estable ejecutable).
* **Ramas de Trabajo:**
  - `Hernan-features`
  - `fredy-feature`
  - `junior-feature`
* **Flujo de Trabajo:**
  1. Cada integrante trabaja en su rama (`feature/xyz`).
  2. Commits frecuentes con mensajes descriptivos (ej: `feat: ...`, `fix: ...`).
  3. Crear Pull Request (PR) rapido a `main` antes de la demo.
