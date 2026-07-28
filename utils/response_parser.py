import re
from typing import Dict


def parse_stages(response: str) -> Dict[str, str]:
    """Parsea la respuesta del agente en las 3 etapas predefinidas de forma robusta.

    Args:
        response: Respuesta completa en formato Markdown del agente.

    Returns:
        Diccionario con las 3 etapas parseadas ("diagnostico", "variante", "cita").
    """
    if not response or not isinstance(response, str):
        return {"diagnostico": "", "variante": "", "cita": ""}

    response_text = response.strip()
    stages = {"diagnostico": "", "variante": "", "cita": ""}

    match1 = re.search(r"(?i)(?:###?\s*|\*\*|)?etapa\s*1", response_text)
    match2 = re.search(r"(?i)(?:###?\s*|\*\*|)?etapa\s*2", response_text)
    match3 = re.search(r"(?i)(?:###?\s*|\*\*|)?etapa\s*3|📑", response_text)

    if match1:
        start_1 = match1.start()
        header_end = response_text.find("\n", start_1)
        content_start_1 = header_end + 1 if header_end != -1 else start_1
        end_1 = match2.start() if match2 else (match3.start() if match3 else len(response_text))
        stages["diagnostico"] = response_text[content_start_1:end_1].strip()

    if match2:
        start_2 = match2.start()
        header_end = response_text.find("\n", start_2)
        content_start_2 = header_end + 1 if header_end != -1 else start_2
        end_2 = match3.start() if match3 else len(response_text)
        stages["variante"] = response_text[content_start_2:end_2].strip()

    if match3:
        start_3 = match3.start()
        if response_text[start_3:].startswith("📑"):
            stages["cita"] = response_text[start_3:].strip()
        else:
            header_end = response_text.find("\n", start_3)
            content_start_3 = header_end + 1 if header_end != -1 else start_3
            stages["cita"] = response_text[content_start_3:].strip()

    # Limpiar encabezados Markdown residuales (ej. '###') al final de cada bloque
    for k in ["diagnostico", "variante", "cita"]:
        stages[k] = re.sub(r"\n*###?\s*$", "", stages[k]).strip()

    # Fallback robusto si la LLM respondió en texto plano sin etiquetas explícitas ETAPA 1/ETAPA 2
    if not stages["diagnostico"] and not stages["variante"]:
        if "📑" in response_text:
            parts = response_text.split("📑", 1)
            stages["diagnostico"] = parts[0].strip()
            stages["cita"] = "📑 " + parts[1].strip()
        else:
            stages["diagnostico"] = response_text

    return stages
