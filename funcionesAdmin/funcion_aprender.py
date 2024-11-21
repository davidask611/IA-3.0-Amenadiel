# from stopwords import stopwords_spanish
import json
from difflib import get_close_matches
from funciones.funcion_eliminarAcentos import eliminar_acentos
import os
from funcionesAdmin.manejo_archivos import process_json, process_txt, process_pdf
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

# Cargar el modelo de español
nlp = spacy.load('es_core_news_sm')

# Probar el modelo con una frase
# doc = nlp("Hola, este es un ejemplo de procesamiento de texto con spaCy.")
# for token in doc:
#     print(f"{token.text} -> {token.pos_}")


def cargar_stopwords(ruta='stopwords.txt'):
    try:
        # Calcula la ruta basada en la ubicación del script actual
        ruta_absoluta = os.path.join(os.path.dirname(__file__), ruta)
        with open(ruta_absoluta, 'r', encoding='utf-8') as archivo:
            # Carga las palabras en un set
            return set(archivo.read().splitlines())
    except Exception as e:
        print(f"Error al cargar stopwords: {e}")
        return set()


# Cargar las stopwords desde el archivo en la carpeta actual
stopwords_spanish = cargar_stopwords('stopwords.txt')


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


estado_confirmacion = {}


def entrenando_IA(pregunta_limpia, datos_previos, modo_administrador=False, cutoff_usuario=0.5, cutoff_admin=0.7, esperando_confirmacion=None):

    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())
    print(f"Pregunta procesada: {pregunta_limpia}")

    global estado_confirmacion

    # Verifica si ya hay una confirmación pendiente
    if estado_confirmacion.get("confirmacion_pendiente"):
        return None  # Deja que el flujo de Flask maneje la confirmación

    # Verifica si ya se está esperando una confirmación
    if esperando_confirmacion:
        if pregunta_limpia == "sí":
            # Mostrar categorías disponibles para guardar
            categorias = list(datos_previos["publico"].keys())
            print("Categorías disponibles:", categorias)
            return f"Selecciona una categoría para guardar: {', '.join(categorias)}", esperando_confirmacion

        elif pregunta_limpia in datos_previos["publico"]:
            # Guardar la respuesta en la categoría seleccionada
            datos_previos["publico"][pregunta_limpia][esperando_confirmacion["pregunta"]
                                                      ] = esperando_confirmacion["respuesta"]
            guardar_datos(datos_previos)
            print("Respuesta confirmada y guardada en la categoría:", pregunta_limpia)
            return f"Respuesta guardada en la categoría '{pregunta_limpia}'.", None

        elif pregunta_limpia == "no":
            # Rechazo de la respuesta
            print(f"Intentos actuales: {esperando_confirmacion['intentos']}")
            return f"La propuesta fue rechazada. Intenta preguntar de otra manera o carga datos relacionados con '{esperando_confirmacion['pregunta']}'.", None

    # Selección de la sección según el rol (modo_administrador)
    seccion = "entrenamiento" if modo_administrador else "publico"
    cutoff = cutoff_admin if modo_administrador else cutoff_usuario

    # Función interna para buscar en la sección de datos previos
    def buscar_en_seccion(seccion, cutoff):
        print(f"Buscando en la sección '{seccion}' con cutoff {cutoff}")
        if seccion not in datos_previos:
            print(f"Sección '{seccion}' no encontrada en datos_previos.")
            return []

        resultados = []
        for categoria, contenido in datos_previos.get(seccion, {}).items():
            if isinstance(contenido, dict):
                respuesta_exacta = contenido.get(pregunta_limpia)
                if respuesta_exacta:
                    print(f"Respuesta exacta encontrada: {respuesta_exacta}")
                    return [respuesta_exacta]
                mejor_coincidencia = get_close_matches(
                    pregunta_limpia, contenido.keys(), n=1, cutoff=cutoff)
                if mejor_coincidencia:
                    resultados.append(contenido[mejor_coincidencia[0]])
            elif isinstance(contenido, list):
                for frase in contenido:
                    if pregunta_limpia in frase.lower():
                        resultados.append(frase)
        return resultados

    resultados = buscar_en_seccion(seccion, cutoff)
    if resultados:
        return f"Respuesta encontrada en {seccion.capitalize()}: <br><br>{resultados[0]}"

    if modo_administrador:
        print("Modo administrador activo. Buscando en archivos...")
        archivos_en_uploads = os.listdir('uploads')
        print("Archivos detectados en 'uploads':", archivos_en_uploads)
        resultados_archivos = []
        nlp = spacy.load('es_core_news_sm')

        for nombre_archivo in archivos_en_uploads:
            ruta_archivo = os.path.join('uploads', nombre_archivo)
            # Aquí estamos mostrando el archivo que se está procesando.
            print(f"Procesando archivo: {nombre_archivo}")

            if nombre_archivo.endswith('.json'):
                datos = process_json(ruta_archivo)
                if isinstance(datos, dict):
                    for clave, valor in datos.items():
                        if pregunta_limpia in str(clave).lower() or pregunta_limpia in str(valor).lower():
                            # Aquí mostramos la coincidencia encontrada.
                            print(f"Coincidencia encontrada en JSON: {valor}")
                            resultados_archivos.append(valor)
            elif nombre_archivo.endswith('.txt'):
                contenido = process_txt(ruta_archivo)
                frases = contenido.split('.')
                for frase in frases:
                    if pregunta_limpia in frase.lower():
                        # Aquí mostramos la coincidencia encontrada.
                        print(
                            f"Coincidencia encontrada en TXT: {frase.strip()}")
                        resultados_archivos.append(frase.strip())
            elif nombre_archivo.endswith('.pdf'):
                contenido = process_pdf(ruta_archivo)
                frases = contenido.split('.')
                for frase in frases:
                    if pregunta_limpia in frase.lower():
                        # Aquí mostramos la coincidencia encontrada.
                        print(
                            f"Coincidencia encontrada en PDF: {frase.strip()}")
                        resultados_archivos.append(frase.strip())

        if resultados_archivos:
            mejor_respuesta = sorted(
                resultados_archivos, key=lambda x: len(x))[0][:500]
            print(f"Mejor respuesta encontrada en archivos: {mejor_respuesta}")

            # Preparar confirmación
            estado_confirmacion = {
                "confirmacion_pendiente": True,
                "pregunta": pregunta_limpia,
                "respuesta": mejor_respuesta,
                "categorias": list(datos_previos["publico"].keys())
            }
            return f"¿Tiene coherencia mi respuesta? '{mejor_respuesta}'. Responde con 'sí' o 'no'."
    print("No se encontró información relevante.")
    return None


def generar_respuesta_por_similitud(pregunta_limpia, datos_previos):
    # Asegurarse que la pregunta esté en minúsculas y limpia de acentos
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

    if not respuestas_posibles:
        return "No hay suficientes datos para generar una respuesta."

    # Añadir la pregunta limpia para compararla
    preguntas_existentes.append(pregunta_limpia)

    # Configuramos el vectorizador para las palabras de parada en español
    vectorizer = TfidfVectorizer(stop_words=stopwords_spanish)
    tfidf_matrix = vectorizer.fit_transform(preguntas_existentes)

    # Calcular las similitudes de coseno entre la última pregunta (pregunta_limpia) y las anteriores
    similitudes = np.dot(tfidf_matrix[-1], tfidf_matrix[:-1].T).toarray()

    # Obtener el índice de la máxima similitud
    indice_similitud_maxima = similitudes.argmax()
    puntaje_similitud = similitudes[0, indice_similitud_maxima]

    # Establecer un umbral mínimo de similitud (opcional)
    umbral_similitud = 0.5
    if puntaje_similitud < umbral_similitud:
        return "No se encontró una respuesta relevante."

    # Devolver la respuesta más similar
    respuesta_similar = respuestas_posibles[indice_similitud_maxima]
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
                # Convertimos stopwords_spanish (set) a una lista
                vectorizer = TfidfVectorizer(
                    stop_words=list(stopwords_spanish))

                tfidf_matrix = vectorizer.fit_transform(
                    textos_resultados + [pregunta_limpia])
                similitudes = cosine_similarity(
                    tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

                # Encuentra el índice con la mayor similitud
                indice_similitud_maxima = similitudes.argmax()

                # Establecer un umbral mínimo de similitud (opcional)
                umbral_similitud = 0.5
                if similitudes[indice_similitud_maxima] < umbral_similitud:
                    resultados.append(
                        "No se encontró una coincidencia relevante.")
                else:
                    resultados.append(
                        f"Coincidencia más relevante en {nombre_archivo}: {textos_resultados[indice_similitud_maxima]}")

        except Exception as e:
            print(f"Error al procesar el archivo {nombre_archivo}: {e}")

    # Si no hay resultados, puede ser útil ofrecer un mensaje adicional
    if not resultados:
        return f"No se encontraron coincidencias relevantes en los archivos cargados para: {pregunta_limpia}."

    return resultados
