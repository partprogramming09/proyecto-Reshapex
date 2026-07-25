# ⚡ Engine Context & Documentation — LS Electric AI Agent

Documentación completa del contexto, arquitectura, regla de negocio y stack técnico para la Hackatón **AgentSprint (ReshapeX)**.

---

## 📌 1. Información General de la Hackatón

* **Evento:** AgentSprint — AI Hackathon por ReshapeX.
* **Lugar / Fecha:** Universidad EAFIT, Medellín · 8:00 AM – 12:00 PM.
* **Formato:** ~3.5 horas de desarrollo continuo en equipos de 3 a 4 integrantes.
* **Empresa / Marca Seleccionada:** **LS Electric** (Líder en Automatización Industrial y Control de Potencia).
* **Premios:** 🥇 $2.000.000 COP | 🥈 $1.000.000 COP | 🥉 $500.000 COP.

### Criterios de Evaluación (100% Total):
1. **Progreso / Hitos (30%):** De Setup inicial a Respuestas Fundamentadas (Grounded) con herramientas/manuales.
2. **Innovación (30%):** Originalidad y utilidad real para la industria OEM.
3. **Checklist Técnico (20%):** Funcionamiento real de los componentes (Tools, RAG, Loop, Guardrails) en código.
4. **Calidad de Código y Git (10%):** Repositorio limpio, sin claves expuestas (`.env`), commits ordenados.
5. **Pitch & Presentación (10%):** Demo en vivo de 2 minutos limpia y respuesta a jurados.

---

## 🏢 2. Contexto de Negocio: LS Electric (OEM)

**LS Electric** fabrica equipos de automatización de alta gama:
* **Variadores de Frecuencia (VFD / Inverters):** Series iG5A (descontinuado/obsoleto popular), S100 (Estándar), H100 (HVAC/Bombas), M100 (Micro).
* **PLCs y HMIs:** Serie XGB, XGK e iXP2.

### El Problema de Negocio Solucionado:
Los ingenieros y técnicos de planta se enfrentan a:
1. Paradas de planta por códigos de falla en variadores (ej. `OCT`, `OVT`, `ETH`, `NTC`).
2. Necesidad urgente de sustituir variadores viejos (iG5A) por series actuales (S100/H100) manteniendo potencia, voltaje y dimensiones.

---

## 🔄 3. Regla de Negocio Constante (Flujo en 3 Etapas)

El agente opera bajo una arquitectura de 3 etapas secuenciales y obligatorias:

```
+-------------------------------------------------------------------+
|                     ETAPA 1: GUÍA TÉCNICA 🔍                      |
| Consultar Manuales y BBDD de Fallas (OCT, OVT, ETH, NTC)          |
+--------------------------------─┬─────────────────────────────────+
                                  |
                                  v
+-------------------------------------------------------------------+
|                ETAPA 2: VARIANTES Y SUSTITUTOS ⚙️                 |
| Evaluar Matriz de Migración (ej. iG5A 5.5kW -> S100-4 5.5kW)       |
+--------------------------------─┬─────────────────────────────────+
                                  |
                                  v
+-------------------------------------------------------------------+
|             ETAPA 3: RESPUESTA GROUNDED CON CITA 📑               |
| Sintetizar respuesta en Markdown citando Manual, Sección y Pág.   |
+-------------------------------------------------------------------+
```

### Detalle de las Etapas:
1. **Etapa 1 (Consulta de Guía):** Identifica el código de error, la causa raíz y la lista de acciones correctivas recomendadas.
2. **Etapa 2 (Revisión de Variantes):** Mapea el modelo consultado contra el catálogo de sustitución directa/premium y especifica compatibilidad de montaje.
3. **Etapa 3 (Cita de Origen):** Genera la respuesta en Markdown incluyendo obligatoriamente la cita formal (`📑 Cita Oficial del Manual: Manual X, Sección Y, Pág. Z`).

---

## 🛠️ 4. Estructura del Código y Archivos del Proyecto

* [`agent_engine.py`](file:///C:/JUNIOR/Proyectos%20Personales/proyecto-Reshapex/agent_engine.py): Motor central del agente en Python.
  * Integra la API oficial `google-genai` con fallback inteligente entre `gemini-2.0-flash` y `gemini-1.5-flash`.
  * Contiene la base de conocimiento en memoria de manuales y la matriz de variantes LS Electric.
* [`app.py`](file:///C:/JUNIOR/Proyectos%20Personales/proyecto-Reshapex/app.py): Aplicación Web interactiva en Streamlit.
  * Tema visual oscuro ajustado a las guías de diseño de ReshapeX.
  * Inspección en tiempo real de las 3 etapas del pipeline.
  * Presets de preguntas rápidas.
* [`test_demo.py`](file:///C:/JUNIOR/Proyectos%20Personales/proyecto-Reshapex/test_demo.py): Script de prueba unitaria sin interfaz gráfica.
* [`requirements.txt`](file:///C:/JUNIOR/Proyectos%20Personales/proyecto-Reshapex/requirements.txt): Dependencias necesarias (`google-genai`, `streamlit`, `python-dotenv`).
* [`.gitignore`](file:///C:/JUNIOR/Proyectos%20Personales/proyecto-Reshapex/.gitignore): Configuración de seguridad para no subir claves o temporales.
* [`.skills/OEM-Agent-Workflow/SKILL.md`](file:///C:/JUNIOR/Proyectos%20Personales/proyecto-Reshapex/.skills/OEM-Agent-Workflow/SKILL.md): Especificación de la Skill personalizada.

---

## 🚀 5. Guía de Instalación y Ejecución

### Requisitos Previos:
Python 3.10 o superior instalado.

### 1. Instalación de Dependencias:
```bash
pip install -r requirements.txt
```

### 2. Configuración de Variables de Entorno:
Crear un archivo `.env` en la raíz del proyecto (opcional si se ingresa la clave desde la interfaz):
```env
GEMINI_API_KEY=tu_api_key_de_google_ai_studio
```

### 3. Ejecución de la Aplicación Web (Streamlit):
Asegúrate de estar en la carpeta del proyecto antes de ejecutar:
```bash
cd "C:\JUNIOR\Proyectos Personales\proyecto-Reshapex"
streamlit run app.py
```

### 4. Ejecución del Test Unitario:
```bash
python test_demo.py
```

---

## 🌿 6. Estrategia de Trabajo en Git

* **Rama Principal:** `main` (Código estable ejecutable).
* **Rama de Trabajo Actual:** `junior-feature`.
* **Flujo de Trabajo:**
  1. Cada integrante trabaja en su rama (`feature/xyz`).
  2. Commits frecuentes con mensajes descriptivos (ej: `feat: ...`, `fix: ...`).
  3. Crear Pull Request (PR) rápido a `main` antes de la demo.
