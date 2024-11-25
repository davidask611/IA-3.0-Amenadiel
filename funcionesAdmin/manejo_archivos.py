import json
import pdfplumber
import os


def ensure_directory_exists(directory):
    """Asegura que el directorio exista, creándolo si es necesario."""
    os.makedirs(directory, exist_ok=True)


def process_json(file_path):
    """Procesa un archivo JSON y devuelve su contenido como un diccionario."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"error": "El archivo JSON no es válido"}


def process_txt(file_path):
    """Lee el contenido de un archivo TXT."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return {"error": f"Error al leer el archivo TXT: {str(e)}"}


def process_pdf(file_path):
    """Procesa un archivo PDF y extrae su contenido como texto."""
    try:
        # Extraer texto del PDF
        with pdfplumber.open(file_path) as pdf:
            content = ''.join(
                (page.extract_text() or '') for page in pdf.pages
            )

        return content  # Devolver el texto extraído directamente

    except Exception as e:
        return {"error": f"Error al procesar el archivo PDF: {str(e)}"}
