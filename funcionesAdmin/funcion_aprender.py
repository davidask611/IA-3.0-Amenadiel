from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import json
from difflib import get_close_matches
from funciones.funcion_eliminarAcentos import eliminar_acentos
import os
# from manejo_archivos import process_json, process_txt, process_pdf
from funcionesAdmin.manejo_archivos import process_json, process_txt, process_pdf

def cargar_datos(nombre_archivo='datos_previos.json'):
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
        return {}
    except json.JSONDecodeError:
        print("Error: Formato inválido en el archivo JSON.")
        return {}

datos_previos = cargar_datos('datos_previos.json')

def guardar_datos(datos, nombre_archivo='datos_previos.json'):
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4)
    except IOError as e:
        print(f"Error al guardar el archivo {nombre_archivo}: {e}")

def entrenando_IA(pregunta_limpia, datos_previos, modo_administrador=False):
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())
    seccion = "entrenamiento" if modo_administrador else "publico"

    # Función interna para buscar en la sección de datos previos
    def buscar_en_seccion(seccion):
        if seccion not in datos_previos:
            return []
        resultados = []
        for categoria, contenido in datos_previos.get(seccion, {}).items():
            if isinstance(contenido, dict):
                respuesta_exacta = contenido.get(pregunta_limpia)
                if respuesta_exacta:
                    return [respuesta_exacta]
                mejor_coincidencia = get_close_matches(pregunta_limpia.lower(), contenido.keys(), n=1, cutoff=0.6)
                if mejor_coincidencia:
                    resultados.append(contenido[mejor_coincidencia[0]])
            elif isinstance(contenido, list):
                for frase in contenido:
                    if pregunta_limpia.lower() in frase.lower():
                        resultados.append(frase)
        return resultados

    # Busca en la sección correspondiente (entrenamiento o público)
    resultados = buscar_en_seccion(seccion)
    if resultados:
        return f"Respuesta encontrada en {seccion.capitalize()}: <br><br>{resultados[0]}"

    # En modo administrador: intenta buscar en archivos de uploads
    if modo_administrador:
        print("Intentando buscar respuesta en archivos de carga para el administrador...")
        resultados_archivos = buscar_en_archivos_uploads(pregunta_limpia)
        if resultados_archivos:
            return f"Respuesta encontrada en archivos de carga: <br><br>{resultados_archivos[0]}"

        # Si no encuentra en archivos, sugiere cargar archivos nuevos para el administrador
        print("No se encontró información en las fuentes actuales.")
        return "No se ha encontrado una respuesta en entrenamiento ni en los archivos de carga. Por favor, carga archivos relacionados o agrega la respuesta en el entrenamiento para que esté disponible para futuras consultas."

    # Si es usuario y no encuentra respuesta, muestra un mensaje amigable
    return None


def generar_respuesta_por_similitud(pregunta_limpia, datos_previos):
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())

    respuestas_posibles = []
    for seccion in datos_previos.values():
        if isinstance(seccion, dict):
            for contenido in seccion.values():
                if isinstance(contenido, dict):
                    respuestas_posibles.extend(contenido.values())
                elif isinstance(contenido, list):
                    respuestas_posibles.extend(contenido)

    vectorizer = TfidfVectorizer(stop_words='spanish')
    preguntas_existentes = list(datos_previos.keys())
    preguntas_existentes.append(pregunta_limpia)

    tfidf_matrix = vectorizer.fit_transform(preguntas_existentes)
    similitudes = np.dot(tfidf_matrix[-1], tfidf_matrix[:-1].T).toarray()

    indice_similitud_maxima = similitudes.argmax()
    respuesta_similar = respuestas_posibles[indice_similitud_maxima]
    guardar_datos(datos_previos)

    return respuesta_similar

def buscar_en_archivos_uploads(pregunta_limpia, carpeta_uploads='uploads'):
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())
    resultados = []
    for nombre_archivo in os.listdir(carpeta_uploads):
        ruta_archivo = os.path.join(carpeta_uploads, nombre_archivo)
        if nombre_archivo.endswith('.json'):
            datos = process_json(ruta_archivo)
            # Aquí puedes realizar una búsqueda en los datos JSON cargados
        elif nombre_archivo.endswith('.txt'):
            contenido = process_txt(ruta_archivo)
            # Buscar en el contenido del archivo TXT
        elif nombre_archivo.endswith('.pdf'):
            contenido = process_pdf(ruta_archivo)
            # Buscar en el contenido del archivo PDF
        # Agregar coincidencias al arreglo resultados si se encuentran
    return resultados
