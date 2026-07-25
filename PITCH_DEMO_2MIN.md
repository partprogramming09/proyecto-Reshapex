# 🚀 Pitch & Demo Script (2 Minutos) — LS Electric AI Agent
**Hackathon AgentSprint (ReshapeX) · Universidad EAFIT**

---

## 📌 Resumen Ejecutivo del Pitch

| Parámetro | Detalle |
| :--- | :--- |
| **Empresa / Cliente** | **LS Electric** (Automatización Industrial & Control de Potencia) |
| **Problema** | Paradas de planta industriales costosas por fallas en variadores de frecuencia y dificultad para migrar equipos obsoletos (`iG5A`) a series actuales (`S100` / `H100`). |
| **Solución** | Agente de IA Industrial con arquitectura RAG en **3 etapas obligatorias** (Diagnóstico → Recomendación de Variantes → Cita Grounded de Origen). |
| **Stack Técnico** | Python, Streamlit, LlamaIndex Core, Google Gemini (`gemini-3.1-flash-lite`), ChatMemoryBuffer y Fallback Multi-Modelo. |

---

## ⏱️ Cronograma de Presentación en Vivo (2 Minutos Exactos)

```
0:00 - 0:30 ───> 1. El Problema en Planta & Hook
0:30 - 1:15 ───> 2. Demo en Vivo (Consulta RAG de 3 Etapas)
1:15 - 1:45 ───> 3. Memoria Conversacional & Modo Autónomo
1:45 - 2:00 ───> 4. Cierre de Alto Impacto
```

---

### 1. El Problema en Planta & Hook (0:00 – 0:30)

> 🎙️ **Voz del Presentador:**
> *"Buenas tardes jurados. En una planta de manufactura, **cada minuto de parada cuesta miles de dólares**. Cuando un variador de frecuencia falla con un código como `OCT` o `OVT`, los ingenieros de mantenimiento pierden horas buscando en manuales de 500 páginas o intentando reemplazar un equipo obsoleto como el `iG5A` que ya no se fabrica.*
> 
> *Presentamos a **LS Electric AI Agent**: el primer asistente inteligente industrial que diagnostica fallas, recomienda la migración exacta de equipos y cita oficialmente la página y manual del fabricante en menos de 5 segundos."*

---

### 2. Demo en Vivo: Flujo RAG en 3 Etapas (0:30 – 1:15)

> 🎙️ **Voz del Presentador (Mientras escribe o selecciona Preset 1 en la pantalla):**
> *"Vamos a probarlo en vivo. Ingresemos esta falla real de planta:*
> 
> 💬 **Query en pantalla:** `"Tengo un error OCT en mi variador iG5A de 5.5kW al acelerar"`
> 
> *Observemos cómo el agente responde bajo una **estricta regla de negocio en 3 etapas:**"*

1. **🛠️ Etapa 1 - Diagnóstico Técnico:** Identifica el disparo por sobrecorriente (*Overcurrent Trip*), explica la causa raíz en la rampa de aceleración `ACC` y entrega la lista de verificación paso a paso.
2. **⚙️ Etapa 2 - Recomendación & Variantes:** Detecta que el `iG5A` es una serie descontinuada y recomienda la sustitución por la serie **LS Electric S100-4 de 5.5kW**, especificando compatibilidad de montaje.
3. **📑 Etapa 3 - Cita de Origen Grounded:** Genera la cita oficial formal del manual (`Manual LS Electric, Cap 4, Pág 12`) o fuente verificada.

---

### 3. Memoria Conversacional & Resiliencia Autónoma (1:15 – 1:45)

> 🎙️ **Voz del Presentador (Ejecuta la segunda consulta secuencial):**
> *"El agente no responde aislado; cuenta con **memoria a corto plazo modularizada (`ChatMemoryBuffer`)**.*
> 
> 💬 **Query 2 en pantalla:** `"¿Cuál era el modelo de sustitución que me recomendaste en la respuesta anterior?"`
> 
> *El agente recuerda el contexto sin repetir la búsqueda y confirma de inmediato la serie `S100`.*
> 
> *Además, cuenta con **resiliencia autónoma (Fallback Chain)**: si no hay documentos locales cargados, el agente opera con conocimiento especializado en automatización industrial manteniendo la estructura de 3 etapas y aplicando guardrails para ignorar consultas off-topic."*

---

### 4. Cierre de Alto Impacto (1:45 – 2:00)

> 🎙️ **Voz del Presentador:**
> *"Con **LS Electric AI Agent**, transformamos la documentación técnica pasiva en **resolución instantánea y grounded** para la industria OEM. Reducimos el tiempo de diagnóstico de horas a segundos.*
> 
> *¡Muchas gracias! Quedamos atentos a sus preguntas."*

---

## ❓ Preguntas Frecuentes de los Jurados (Q&A Prep)

### Q1: ¿Cómo evitan que el modelo alucine o invente manuales que no existen?
> **Respuesta:** Implementamos un **RAG estricto con LlamaIndex** y un System Prompt respaldado por el motor en 3 etapas. Si la información no se encuentra en el manual PDF indexado o fuente oficial, el agente indica explícitamente que la fuente no ha sido verificada o que se requiere consultar el soporte técnico oficial de LS Electric.

### Q2: ¿Qué pasa si el servicio de la API de Gemini falla durante la demostración?
> **Respuesta:** Contamos con un patrón de diseño **Chain of Responsibility (Fallback Agent)** que conmuta automáticamente entre 3 modelos de respaldo (`gemini-3.1-flash-lite`, `gemini-3.5-flash-lite`, `gemma-4-26b-a4b-it`) e incluye caché MD5 en memoria RAM.

### Q3: ¿Cómo manejan el límite de tokens en conversaciones largas?
> **Respuesta:** Modularizamos la memoria en una clase dedicada (`AgentMemoryManager`) que utiliza `ChatMemoryBuffer` con un límite estricto de 3,000 tokens de entrada, recortando de forma inteligente los turnos más antiguos sin perder el contexto reciente.

---

## 🛠️ Checklist Pre-Pitch para la Demo
- [ ] Tener la app corriendo localmente: `streamlit run app.py`
- [ ] Tener al menos 1 PDF de manual en `data/raw/` (para mostrar la insignia 🟢 Modo RAG Activo).
- [ ] Tener a la mano la consulta preset: `"Tengo un error OCT en mi variador iG5A de 5.5kW al acelerar"`.
- [ ] Navegador en pantalla completa y zoom a 110% para lectura clara de los jurados.
