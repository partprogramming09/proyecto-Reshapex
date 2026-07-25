## 📌 1. Resumen del Evento

• Evento: AgentSprint — AI Hackathon por ReshapeX.
• Lugar: Universidad EAFIT, Medellín.
• Duración: ~3.5 horas de código continuo (8:00 AM – 12:00 PM).
• Equipos: 3 a 4 integrantes.
• Premios: 🥇 $2.000.000 COP | 🥈 $1.000.000 COP | 🥉 $500.000 COP.
• Tema Principal: Agentes de IA aplicados a fabricantes e industria (OEMs - Original Equipment
Manufacturers).
──────

## 🏢 2. Tu Empresa Seleccionada: LS ELECTRIC

LS Electric es un gigante global de automatización industrial y electricidad (Corea del Sur). Sus
productos estrella son:

1. Variadores de Frecuencia (VFD / Inverters): Series iG5A (muy popular, muchos descontinuados), S100,
   H100, i5, G100.
2. PLCs y Pantallas HMI: Serie XGB, XGK, iXP2.
3. Interruptores y Contactores Electrónicos: Metasol ACB/MCCB.

### 💡 Caso de Uso Ganador para LS Electric:

Un Asistente Técnico y Comercial de Automatización Industrial:

• Problema: Un técnico de planta tiene un variador LS Electric arrojando un error (ej: OCT -
Overcurrent, OVT - Overvoltage) o necesita reemplazar un modelo viejo/descontinuado (ej. iG5A) por uno
moderno (ej. S100) en medio de una parada de planta.
• Solución del Agente: El agente lee la falla o especificación, consulta la base de
conocimiento/catálogo (RAG/Tools), entrega el diagnóstico exacto con página de manual citada, y
sugiere el reemplazo directo con coincidencia de HP, voltaje y cableado.
──────

## 📊 3. Matriz de Evaluación (¿Cómo se gana?)

Dimensión │ Peso │ ¿En qué se fijan los jurados?
───────────────────────┼──────┼───────────────────────────────────────────────────────────────────────
Progreso (Milestones) │ 30% │ Alcanzar hitos: 1 pt (Setup listo) ➔ 2 pts (Algo funciona) ➔ 3 pts
│ │ (Demo en vivo) ➔ 4 pts (Respuestas 100% fundamentadas en
│ │ herramientas/RAG sin alucinar).
Innovación │ 30% │ Que el caso de uso sea original y realmente útil para la industria,
│ │ no un chatbot genérico.
Checklist Técnico │ 20% │ Que los componentes del agente (Tools, RAG, Loop, Guardrails)
│ │ funcionen de verdad en código (revisan arquitectura real, penalizan
│ │ si está "mockeado").
Calidad de Código / Git │ 10% │ Repositorio limpio, commits frecuentes (¡usar la rama junior-
│ │ feature!), sin claves expuestas (.env), sin código de mentiras.
Presentación / Pitch │ 10% │ Demo de 2 minutos fluida, respuesta segura a preguntas de los 5
│ │ jurados.
──────

## 🛠️ 4. Stack Tecnológico Sugerido e Instalación

Como ya tienen la API Key de Gemini, usaremos el Default Stack oficial recomendado por la guía:

    ┌─────────────────────────────────────────────────────────────┐
    │                       Interfaz Web                          │
    │               Streamlit (Python UI rápida)                  │
    └──────────────────────────────┬──────────────────────────────┘
                                   │
    ┌──────────────────────────────▼──────────────────────────────┐
    │                    Cerebro / Agente (Loop)                  │
    │        Google Gemini API + Function Calling (SDK Oficial)   │
    └──────────────┬──────────────────────────────┬───────────────┘
                   │                              │
    ┌──────────────▼──────────────┐ ┌─────────────▼──────────────┐
    │    Herramientas (Tools)     │ │   Base de Conocimiento RAG   │
    │ Catálogo / Buscador de Partes│ │ Manuales PDF LS Electric   │
    │  (Python functions local)   │ │  (ChromaDB / LlamaIndex)   │
    └─────────────────────────────┘ └────────────────────────────┘

### 📦 Qué debe instalar CADA integrante en su PC (Checklist previo):

Ejecuta este comando en la terminal de tu PC para instalar las librerías necesarias:

    pip install google-genai streamlit chromadb llama-index python-dotenv

1. Python 3.10+: Asegurarse de tener Python actualizado (python --version).
2. google-genai / google-generativeai: Para conectar con Gemini 2.0 / 1.5 Flash.
3. streamlit: Para construir la pantalla web interactiva en menos de 30 líneas de Python.
4. chromadb o llama-index (opcional para RAG): Si van a subir PDFs de manuales de LS Electric.
5. python-dotenv: Para cargar la GEMINI_API_KEY desde un archivo .env privado sin subirla a Git.
   ──────

## ⏱️ 5. Plan de Acción para las 3.5 Horas (Time Budget)

    [ 00m - 25m ] ──► Alineación de idea y estructura base
    [ 25m - 100m ] ──► Desarrollo en Paralelo (Gemini + RAG + UI)
    [100m - 150m ] ──► Integración, citas de origen y Guardrails
    [150m - 185m ] ──► Pulir Streamlit UI + Ensayar Pitch de 2 min

1. Primeros 25 min (Todos juntos):
   • Definir la frase clave: "Nuestro agente ayuda a ingenieros de planta a diagnosticar fallas y
   encontrar sustitutos de variadores LS Electric usando manuales técnicos y tabla de equivalencias."
   • Crear archivo .env local con GEMINI_API_KEY=tu_clave.
2. Siguientes 75 min (Trabajo divido entre el equipo):
   • Integrante 1 (Backend/Gemini): Crea el loop del agente con Gemini y define las Functions/Tools
   (ej: buscar_equivalente(modelo_viejo), diagnosticar_falla(codigo_error)).
   • Integrante 2 (Datos/RAG): Descarga 2 o 3 PDFs clave de variadores LS Electric (ej. manual de
   usuario iG5A y S100) y los carga a ChromaDB / LlamaIndex.
   • Integrante 3 (Frontend UI): Crea la interfaz en Streamlit con el chat, selectores de producto y
   área para mostrar las respuestas del agente.
3. Siguientes 50 min (Integración y Confianza):
   • Probar el flujo completo. Asegurar que cuando el agente responda un código de error, cite la
   página del manual o la fuente de datos.
4. Últimos 35 min (Demo y Pitch):
   • ¡Cero nuevas características! Congelar código, probar la demo en la interfaz de Streamlit y
   ensayar la presentación de 2 minutos.

──────

## 🏁 Próximos Pasos Inmediatos

1. Instalar la lista de librerías (pip install google-genai streamlit ...).
2. Probar una llamada "Hello World" a Gemini en un script de prueba.
3. Descargar 1 o 2 manuales técnicos de LS Electric en PDF para tener datos reales listos.

¿Quieres que creemos un script base en Python con Gemini + Streamlit en este repositorio para dejar la
plantilla lista antes del evento?
