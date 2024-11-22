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


def process_pdf(file_path, output_dir='uploads'):
    """Convierte un PDF a texto y guarda el contenido en un archivo .txt."""
    try:
        # Asegurar que el directorio exista
        ensure_directory_exists(output_dir)

        # Extraer texto del PDF
        with pdfplumber.open(file_path) as pdf:
            content = ''.join(
                (page.extract_text() or '') for page in pdf.pages
            )

        # Guardar el texto extraído como archivo .txt
        output_txt_path = os.path.join(output_dir, os.path.splitext(
            os.path.basename(file_path))[0] + '.txt')
        with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(content)

        # print(f"PDF convertido y guardado en: {output_txt_path}")
        return content

    except Exception as e:
        return {"error": f"Error al procesar el archivo PDF: {str(e)}"}
