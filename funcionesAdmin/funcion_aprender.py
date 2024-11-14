from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
# import os
import json
from difflib import get_close_matches
from funciones.funcion_eliminarAcentos import eliminar_acentos

def cargar_datos(nombre_archivo='datos_previos.json'):
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)  # Cargar datos del archivo JSON
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
        return {}  # Retorna un diccionario vacío si no se encuentra el archivo
    except json.JSONDecodeError:
        print("Error: Formato inválido en el archivo JSON.")
        return {}  # Retorna un diccionario vacío si hay un error de formato


datos_previos = cargar_datos('datos_previos.json')

def guardar_datos(datos, nombre_archivo='datos_previos.json'):
    """Guarda los datos actualizados en el archivo JSON."""
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4)
    except IOError as e:
        print(f"Error al guardar el archivo {nombre_archivo}: {e}")

guardar_datos(datos_previos)

def entrenando_IA(pregunta_limpia, datos_previos, modo_administrador=False):
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())
    """
    Función que busca una respuesta en los datos_previos para una pregunta específica.
    Sigue un flujo diferente para usuario y administrador.
    """
    seccion_primaria = "entrenamiento" if modo_administrador else "publico"
    seccion_secundaria = "publico" if modo_administrador else "entrenamiento"
    intentos_restantes = 3 if modo_administrador else 1

    def buscar_en_seccion(seccion):
        if seccion not in datos_previos:
            return []  # Si la sección no existe, no hay resultados.
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

    while intentos_restantes > 0:
        # Busca en la sección primaria
        resultados = buscar_en_seccion(seccion_primaria)
        if resultados:
            return f"Respuesta encontrada en {seccion_primaria.capitalize()}: {resultados[0]}"

        # Si no encontró en la primaria, intenta en la secundaria
        resultados = buscar_en_seccion(seccion_secundaria)
        if resultados:
            return f"Respuesta encontrada en {seccion_secundaria.capitalize()}: {resultados[0]}"

        # Si modo administrador y no encuentra respuesta válida en ambos secciones
        if modo_administrador:
            print(f"Intento {4 - intentos_restantes}/3 para generar respuesta...")
            respuesta_generada = generar_respuesta_por_similitud(pregunta_limpia, datos_previos)
            confirmacion = input(f"Respuesta sugerida: {respuesta_generada}\n¿Es coherente? (si/no): ")
            if confirmacion.lower() == "si":
                mostrar_categorias(datos_previos["publico"], pregunta_limpia, respuesta_generada)
                return f"Respuesta confirmada: {respuesta_generada}"
            intentos_restantes -= 1

        if not modo_administrador or intentos_restantes == 0:
            return "No encontré una respuesta. Por favor, enséñame la respuesta correcta."

    return "No se ha encontrado información relacionada."

def generar_respuesta_por_similitud(pregunta_limpia, datos_previos):
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())

    """
    Genera una respuesta por similitud usando TF-IDF.
    """
    # Extraer las respuestas disponibles de los datos previos
    respuestas_posibles = []
    for seccion in datos_previos.values():
        if isinstance(seccion, dict):
            for contenido in seccion.values():
                if isinstance(contenido, dict):
                    respuestas_posibles.extend(contenido.values())
                elif isinstance(contenido, list):
                    respuestas_posibles.extend(contenido)

    # Crear un vectorizador TF-IDF
    vectorizer = TfidfVectorizer(stop_words='spanish')

    # Combina las preguntas existentes y la nueva pregunta en un solo conjunto de datos
    preguntas_existentes = list(datos_previos.keys())
    preguntas_existentes.append(pregunta_limpia)

    # Transforma las preguntas en vectores TF-IDF
    tfidf_matrix = vectorizer.fit_transform(preguntas_existentes)

    # Calcula la similitud coseno entre la nueva pregunta y las preguntas previas
    similitudes = np.dot(tfidf_matrix[-1], tfidf_matrix[:-1].T).toarray()

    # Obtiene la pregunta más similar
    indice_similitud_maxima = similitudes.argmax()
    respuesta_similar = respuestas_posibles[indice_similitud_maxima]
    guardar_datos(datos_previos)

    return respuesta_similar


def mostrar_categorias(publico, pregunta_limpia, respuesta_generada):
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())

    """Muestra categorías disponibles para agregar una nueva respuesta confirmada."""
    print("Elige una categoría para guardar la respuesta o crea una nueva:")
    categorias = list(publico.keys())
    for categoria in categorias:
        print(f"- {categoria}")
    print("- Nueva categoría")

    categoria_seleccionada = input("Selecciona una categoría o ingresa 'Nueva categoría': ").strip()

    if categoria_seleccionada == "Nueva categoría":
        categoria_seleccionada = input("Ingresa el nombre de la nueva categoría: ").strip()
        publico[categoria_seleccionada] = {}

    if categoria_seleccionada not in publico:
        publico[categoria_seleccionada] = {}

    publico[categoria_seleccionada][pregunta_limpia] = respuesta_generada

    # Guardamos los datos actualizados después de la modificación
    guardar_datos(datos_previos)

    print(f"Respuesta guardada en la categoría: {categoria_seleccionada}")