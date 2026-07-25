import io
from pathlib import Path

from pypdf import PdfReader


def extract_file_preview(uploaded_file, lines: int = 10) -> str:
    """Extrae preview de un archivo subido.

    Args:
        uploaded_file: Archivo de Streamlit.
        lines: Numero de lineas a extraer.

    Returns:
        Preview del archivo como string.
    """
    try:
        uploaded_file.seek(0)
        if uploaded_file.name.endswith(".pdf"):
            contenido = uploaded_file.read()
            reader = PdfReader(io.BytesIO(contenido))
            text = ""
            for page in reader.pages[:2]:
                text += page.extract_text() or ""
            uploaded_file.seek(0)
            preview_lines = text.strip().split("\n")[:lines]
            return "\n".join(preview_lines)
        else:
            contenido = uploaded_file.read().decode("utf-8", errors="replace")
            uploaded_file.seek(0)
            return "\n".join(contenido.split("\n")[:lines])
    except Exception as e:
        uploaded_file.seek(0)
        return f"(No se pudo extraer preview: {e})"


def save_file(uploaded_file, destination: Path) -> Path:
    """Guarda un archivo subido en el destino especificado.

    Args:
        uploaded_file: Archivo de Streamlit.
        destination: Directorio destino.

    Returns:
        Ruta del archivo guardado.
    """
    uploaded_file.seek(0)
    filepath = destination / uploaded_file.name
    filepath.write_bytes(uploaded_file.read())
    uploaded_file.seek(0)
    return filepath
