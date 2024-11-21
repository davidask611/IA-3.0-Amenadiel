import json
import pdfplumber
import os


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


def process_pdf(file_path, output_dir='uploads'):
    try:
        # Asegurarse de que el directorio exista, si no, crear
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Abrir el archivo PDF y extraer el texto
        with pdfplumber.open(file_path) as pdf:
            content = ''.join([
                (page.extract_text() or '').encode(
                    'utf-8', 'ignore').decode('utf-8', 'ignore')
                for page in pdf.pages if page.extract_text()
            ])

        # Definir la ruta del archivo TXT a guardar
        nombre_archivo_txt = os.path.splitext(
            os.path.basename(file_path))[0] + '.txt'
        output_txt_path = os.path.join(output_dir, nombre_archivo_txt)

        # Guardar el contenido extraído en un archivo .txt
        with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(content)

        print(f"PDF convertido y guardado en: {output_txt_path}")
        return content  # Regresar el contenido del archivo procesado como texto

    except Exception as e:
        return {"error": f"Error al procesar el archivo PDF: {str(e)}"}
