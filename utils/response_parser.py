import re
from typing import Dict


def parse_stages(response: str) -> Dict[str, str]:
    """Parsea la respuesta del agente en las 3 etapas.

    Args:
        response: Respuesta completa del agente.

    Returns:
        Diccionario con las 3 etapas parseadas.
    """
    stages = {"diagnostico": "", "variante": "", "cita": ""}
    patterns = [
        (r"(?i)etapa\s*1[^:]*:\s*(.*?)(?=etapa\s*2|recomendación|⚙️|$)", "diagnostico"),
        (r"(?i)etapa\s*2[^:]*:\s*(.*?)(?=etapa\s*3|cita|📑|$)", "variante"),
        (r"(?i)(📑.*$)", "cita"),
    ]
    for pattern, key in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            stages[key] = match.group(1).strip()
    if not stages["cita"]:
        match_cita = re.search(r"📑.*", response, re.DOTALL)
        if match_cita:
            stages["cita"] = match_cita.group(0).strip()
    if not any(stages.values()):
        parts = response.split("\n\n")
        if len(parts) >= 3:
            stages["diagnostico"] = parts[0]
            stages["variante"] = parts[1]
            stages["cita"] = "\n\n".join(parts[2:])
        elif len(parts) == 2:
            stages["diagnostico"] = parts[0]
            stages["cita"] = parts[1]
        else:
            stages["diagnostico"] = response
    return stages
