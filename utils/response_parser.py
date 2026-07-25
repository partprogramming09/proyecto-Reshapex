import re
from typing import Dict
from dataclasses import dataclass


@dataclass(frozen=True)
class DiagnosticReport:
    """Value Object que representa un reporte de diagnóstico procesado en 3 etapas."""

    diagnostico: str = ""
    variante: str = ""
    cita: str = ""

    @property
    def has_stages(self) -> bool:
        """Retorna True si al menos una etapa fue identificada."""
        return bool(self.diagnostico or self.variante or self.cita)

    def to_dict(self) -> Dict[str, str]:
        """Convierte el objeto a diccionario para compatibilidad de interfaz."""
        return {
            "diagnostico": self.diagnostico,
            "variante": self.variante,
            "cita": self.cita,
        }


def parse_stages(response: str) -> Dict[str, str]:
    """Parsea la respuesta del agente en las 3 etapas predefinidas.

    Args:
        response: Respuesta completa del agente.

    Returns:
        Diccionario con las 3 etapas parseadas ("diagnostico", "variante", "cita").
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

    report = DiagnosticReport(
        diagnostico=stages["diagnostico"],
        variante=stages["variante"],
        cita=stages["cita"],
    )
    return report.to_dict()
