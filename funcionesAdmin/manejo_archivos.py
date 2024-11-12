# manejo_archivos.py

import json
import pdfplumber


def process_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data  # Devuelve el JSON cargado como un diccionario de Python
    except json.JSONDecodeError:
        return {"error": "El archivo JSON no es válido"}


def process_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return {"error": f"Error al leer el archivo TXT: {str(e)}"}


def process_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            content = ''.join([
                (page.extract_text() or '').encode(
                    'utf-8', 'ignore').decode('utf-8', 'ignore')
                for page in pdf.pages if page.extract_text()
            ])
        return content
    except Exception as e:
        return {"error": f"Error al procesar el archivo PDF: {str(e)}"}
