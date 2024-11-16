import json
from difflib import get_close_matches
from funciones.funcion_eliminarAcentos import eliminar_acentos
import os
from funcionesAdmin.manejo_archivos import process_json, process_txt, process_pdf
import os
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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


def entrenando_IA(pregunta_limpia, datos_previos, modo_administrador=False, cutoff_usuario=0.5, cutoff_admin=0.6):
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())
    print(f"Pregunta procesada: {pregunta_limpia}")

    # Selección de la sección según el rol (modo_administrador)
    seccion = "entrenamiento" if modo_administrador else "publico"

    # Determina el cutoff adecuado para el rol
    cutoff = cutoff_admin if modo_administrador else cutoff_usuario

    # Función interna para buscar en la sección de datos previos
    def buscar_en_seccion(seccion, cutoff):
        print(f"Buscando en la sección '{seccion}' con cutoff {cutoff}")
        print(f"Estructura de datos_previos: {datos_previos}")
        if seccion not in datos_previos:
            print(f"Sección '{seccion}' no encontrada en datos_previos.")
            return []

        resultados = []
        for categoria, contenido in datos_previos.get(seccion, {}).items():
            print(
                f"Recorriendo categoría: {categoria}, contenido: {contenido}")
            if isinstance(contenido, dict):  # Para la sección 'publico'
                # Comparación exacta de claves
                respuesta_exacta = contenido.get(pregunta_limpia)
                if respuesta_exacta:
                    print(f"Respuesta exacta encontrada: {respuesta_exacta}")
                    return [respuesta_exacta]
                else:
                    # Si no se encuentra exacta, buscar coincidencia con las claves
                    mejor_coincidencia = get_close_matches(
                        pregunta_limpia.lower(), contenido.keys(), n=1, cutoff=cutoff)
                    if mejor_coincidencia:
                        print(
                            f"Mejor coincidencia encontrada: {mejor_coincidencia[0]} con valor: {contenido[mejor_coincidencia[0]]}")
                        resultados.append(contenido[mejor_coincidencia[0]])
            elif isinstance(contenido, list):  # Para la sección 'entrenamiento'
                for frase in contenido:
                    if pregunta_limpia.lower() in frase.lower():
                        resultados.append(frase)
        return resultados

    # Llamada a la función con el cutoff apropiado
    resultados = buscar_en_seccion(seccion, cutoff)

    if resultados:
        return f"Respuesta encontrada en {seccion.capitalize()}: <br><br>{resultados[0]}"

    # En modo administrador: intenta buscar en archivos de uploads
    if modo_administrador:
        print("Intentando buscar respuesta en archivos de carga para el administrador...")

        # Lista los archivos en la carpeta uploads
        archivos_en_uploads = os.listdir('uploads')
        print(f"Archivos en la carpeta de carga: {archivos_en_uploads}")

        # Procesamos los archivos uno por uno
        resultados_archivos = []
        for nombre_archivo in archivos_en_uploads:
            # Muestra el nombre del archivo
            print(f"Procesando archivo: {nombre_archivo}")
            ruta_archivo = os.path.join('uploads', nombre_archivo)

            if nombre_archivo.endswith('.json'):
                # Procesa archivos JSON
                datos = process_json(ruta_archivo)
                if isinstance(datos, dict):  # Si el archivo JSON es válido
                    # Realiza búsqueda en las claves y valores del JSON
                    for clave, valor in datos.items():
                        if pregunta_limpia in str(clave).lower() or pregunta_limpia in str(valor).lower():
                            resultados_archivos.append(
                                f"Coincidencia en {nombre_archivo}: {valor}")

            elif nombre_archivo.endswith('.txt'):
                # Procesa archivos TXT
                contenido = process_txt(ruta_archivo)
                if isinstance(contenido, str):  # Si el archivo TXT se leyó correctamente
                    if pregunta_limpia in contenido.lower():
                        resultados_archivos.append(
                            f"Coincidencia en {nombre_archivo}: {contenido.strip()}")

            elif nombre_archivo.endswith('.pdf'):
                # Procesa archivos PDF
                contenido = process_pdf(ruta_archivo)
                if isinstance(contenido, str):  # Si el archivo PDF se procesó correctamente
                    if pregunta_limpia in contenido.lower():
                        # Muestra solo los primeros 200 caracteres del contenido
                        resultados_archivos.append(
                            f"Coincidencia en {nombre_archivo}: {contenido[:200]}...")

        if resultados_archivos:
            print("Respuesta encontrada en archivos de carga.")
            return f"Respuesta encontrada en archivos de carga: <br><br>{resultados_archivos[0]}"

        # Si no encuentra en archivos, sugiere cargar archivos nuevos para el administrador
        print("No se encontró información en las fuentes actuales.")
        return "No encontré datos relevantes en los archivos, considera cargar archivos de este tema."


def generar_respuesta_por_similitud(pregunta_limpia, datos_previos):
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())

    respuestas_posibles = []
    preguntas_existentes = []

    # Extraer las preguntas y respuestas de los datos previos
    for seccion in datos_previos.values():
        if isinstance(seccion, dict):
            for contenido in seccion.values():
                if isinstance(contenido, dict):
                    # Extraer respuestas de diccionarios anidados
                    for respuesta in contenido.values():
                        respuestas_posibles.append(respuesta)
                        preguntas_existentes.append(respuesta.lower())
                elif isinstance(contenido, list):
                    # Añadir respuestas de listas
                    for frase in contenido:
                        respuestas_posibles.append(frase)
                        preguntas_existentes.append(frase.lower())

    # Añadir la pregunta limpia para compararla
    preguntas_existentes.append(pregunta_limpia)

    # Crear la matriz TF-IDF
    vectorizer = TfidfVectorizer(stop_words='spanish')
    tfidf_matrix = vectorizer.fit_transform(preguntas_existentes)

    # Calcular las similitudes de coseno
    similitudes = np.dot(tfidf_matrix[-1], tfidf_matrix[:-1].T).toarray()

    # Obtener el índice de la máxima similitud
    indice_similitud_maxima = similitudes.argmax()

    # Devolver la respuesta más similar
    respuesta_similar = respuestas_posibles[indice_similitud_maxima]
    # Guardar cualquier cambio en los datos previos (si es necesario)
    guardar_datos(datos_previos)

    return respuesta_similar


def buscar_en_archivos_uploads(pregunta_limpia, carpeta_uploads='uploads'):
    # Eliminar acentos para comparación
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())
    resultados = []

    # Recorre todos los archivos dentro de la carpeta 'uploads'
    for nombre_archivo in os.listdir(carpeta_uploads):
        ruta_archivo = os.path.join(carpeta_uploads, nombre_archivo)

        try:
            # Verifica el tipo de archivo y procesa según corresponda
            if nombre_archivo.endswith('.json'):
                # Procesa archivos JSON
                datos = process_json(ruta_archivo)
                if isinstance(datos, dict):  # Si el archivo JSON es válido
                    # Realiza búsqueda en las claves y valores del JSON usando expresiones regulares
                    for clave, valor in datos.items():
                        if re.search(pregunta_limpia, str(clave).lower()) or re.search(pregunta_limpia, str(valor).lower()):
                            resultados.append(
                                f"Coincidencia en {nombre_archivo}: {valor}")

            elif nombre_archivo.endswith('.txt'):
                # Procesa archivos TXT
                contenido = process_txt(ruta_archivo)
                if isinstance(contenido, str):  # Si el archivo TXT se leyó correctamente
                    if re.search(pregunta_limpia, contenido.lower()):
                        # Agrega más contexto en la coincidencia
                        resultados.append(
                            f"Coincidencia en {nombre_archivo}: {contenido.strip()}")

            elif nombre_archivo.endswith('.pdf'):
                # Procesa archivos PDF
                contenido = process_pdf(ruta_archivo)
                if isinstance(contenido, str):  # Si el archivo PDF se procesó correctamente
                    if re.search(pregunta_limpia, contenido.lower()):
                        # Muestra solo los primeros 200 caracteres del contenido
                        resultados.append(
                            f"Coincidencia en {nombre_archivo}: {contenido[:200]}...")

            # Si se han encontrado resultados, pasamos a calcular la similitud de coseno con TF-IDF
            if resultados:
                textos_resultados = [resultado.split(
                    ": ", 1)[1] for resultado in resultados]
                vectorizer = TfidfVectorizer(stop_words='spanish')
                tfidf_matrix = vectorizer.fit_transform(
                    textos_resultados + [pregunta_limpia])
                similitudes = cosine_similarity(
                    tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

                # Encuentra el índice con la mayor similitud
                indice_similitud_maxima = similitudes.argmax()
                resultados.append(
                    f"Coincidencia más relevante en {nombre_archivo}: {textos_resultados[indice_similitud_maxima]}")

        except Exception as e:
            print(f"Error al procesar el archivo {nombre_archivo}: {e}")

    # Si no hay resultados, puede ser útil ofrecer un mensaje adicional
    if not resultados:
        return f"No se encontraron coincidencias relevantes en los archivos cargados para: {pregunta_limpia}."

    return resultados
