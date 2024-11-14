import json
import unicodedata
import random
import os
from datetime import datetime
import re
import math
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import get_close_matches
# Y así sucesivamente para cada función
from funciones.funcion_saludo import buscar_saludo
from funciones.funcion_sobreIA import responder_sobre_ia
from funciones.funcion_presidente import presidente
from funciones.funcion_signo import detectar_signo
from funciones.funcion_animales import verificar_musica_animal
from funciones.funcion_comida import comida
from funciones.funcion_chiste import verificar_chiste
from funciones.funcion_chiste import obtener_chiste
from funciones.funcion_matematica import matematica
from funciones.funcion_huerta import huerta
from funciones.funcion_geografia import geografia
from funciones.funcion_eliminarAcentos import eliminar_acentos
from funcionesAdmin.funcion_ver_datos import ver_datos
from funcionesAdmin.funcion_aprender import entrenando_IA
UMBRAL_SIMILITUD = 0.6
historial_preguntas = []  # Contexto/ultima pregunta/categoria
historial_conversacion = []
MAX_HISTORIAL = 10  # Limitar el historial a los últimos 10 mensajes
# TODO zona carga datos
dias_semana = {
    "Monday": "lunes",
    "Tuesday": "martes",
    "Wednesday": "miércoles",
    "Thursday": "jueves",
    "Friday": "viernes",
    "Saturday": "sábado",
    "Sunday": "domingo"
}


def cargar_datos(nombre_archivo='conocimientos.json'):
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)  # Cargar datos del archivo JSON
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
        return {}  # Retorna un diccionario vacío si no se encuentra el archivo
    except json.JSONDecodeError:
        print("Error: Formato inválido en el archivo JSON.")
        return {}  # Retorna un diccionario vacío si hay un error de formato


conocimientos = cargar_datos('conocimientos.json')


def cargar_datos_geografia():
    """
    Carga los datos del archivo `geografia.json`.
    Si el archivo no existe o está vacío, retorna un diccionario vacío.
    """
    try:
        with open("geografia.json", "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return (
            {}
        )  # Si el archivo no existe o está vacío, retornamos un diccionario vacío


geografia_data= cargar_datos_geografia()


def cargar_saludos(conocimientos):
    """Cargar los saludos desde el JSON de conocimientos."""
    return conocimientos.get("saludos", {})


def cargar_json(archivo):
    with open(archivo, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_datos(datos, nombre_archivo='conocimientos.json', mostrar_mensaje=False, verificar_existencia=True):
    if verificar_existencia and not os.path.exists(nombre_archivo):
        print(f"Advertencia: El archivo '{archivo}' no contiene datos válidos o está vacío.")

    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)
        if mostrar_mensaje:
            print(f"Datos guardados exitosamente en '{nombre_archivo}'.")
    except IOError as e:
        print(f"Error al guardar los datos en el archivo '{nombre_archivo}': {e}")



def cargar_animales(nombre_archivo='animales.json'):
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)  # Cargar datos del archivo JSON
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
        return {}  # Retorna un diccionario vacío si no se encuentra el archivo
    except json.JSONDecodeError:
        print("Error: Formato inválido en el archivo JSON.")
        return {}  # Retorna un diccionario vacío si hay un error de formato


animales_data = cargar_animales('animales.json')

def cargar_datos_previos(nombre_archivo='datos_previos.json'):
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)  # Cargar datos del archivo JSON
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
        return {}  # Retorna un diccionario vacío si no se encuentra el archivo
    except json.JSONDecodeError:
        print("Error: Formato inválido en el archivo JSON.")
        return {}  # Retorna un diccionario vacío si hay un error de formato

datos_previos = cargar_datos_previos()

# print(datos_previos)

def actualizar_historial(pregunta, respuesta, conocimientos, animales_data):
    historial_conversacion.append(
        {"pregunta": pregunta, "respuesta": respuesta})

    if len(historial_conversacion) > MAX_HISTORIAL:
        historial_conversacion.pop(0)  # Eliminar el mensaje más antiguo

    if "historialConversacion" not in conocimientos["contexto"]:
        conocimientos["contexto"]["historialConversacion"] = []

    conocimientos["contexto"]["historialConversacion"].append(
        {"pregunta": pregunta, "respuesta": respuesta})

    if len(conocimientos["contexto"]["historialConversacion"]) > MAX_HISTORIAL:
        conocimientos["contexto"]["historialConversacion"].pop(0)

    guardar_datos(conocimientos, 'conocimientos.json')


def calcular_similitud_coseno(pregunta, respuestas):
    # Verificar que haya al menos un elemento en respuestas
    if not respuestas:
        return np.array([])  # Retorna un array vacío si no hay respuestas

    # Crear los vectores con TF-IDF
    vectorizer = TfidfVectorizer().fit_transform([pregunta] + respuestas)

    # Verificar que el vectorizer haya generado más de un vector
    if vectorizer.shape[0] < 2:
        # Retorna un array vacío si solo tiene el vector de la pregunta
        return np.array([])

    # Calcular las similitudes de coseno
    similitudes = cosine_similarity(vectorizer[0:1], vectorizer[1:])
    return similitudes.flatten()


# TODO zona funciones


# Función principal de la IA para procesar mensajes de usuario
def procesar_mensaje(pregunta_limpia, conocimientos, geografia_data, animales_data, datos_previos, es_administrador=False):
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())

    print(f"Procesando mensaje: {pregunta_limpia}, Modo administrador: {es_administrador}")

    if es_administrador and pregunta_limpia == "ver datos":
        contenido = ver_datos(directorio_json='.')
        print("Contenido obtenido:", contenido)
        return contenido if contenido else "No se pudo obtener el contenido."

    # Verificar si es un saludo
    respuesta_saludo = buscar_saludo(pregunta_limpia, conocimientos)
    if respuesta_saludo:
        print("Respuesta de saludo:", respuesta_saludo)
        return respuesta_saludo

    # Intentar responder sobre IA
    respuesta_ia = responder_sobre_ia(pregunta_limpia, conocimientos)
    if respuesta_ia:
        print("Respuesta sobre IA:", respuesta_ia)
        return respuesta_ia

    # Verificar si se pregunta por la hora actual
    if pregunta_limpia in ["que hora es", "que hora es?", "decime la hora", "me decis la hora"]:
        hora_actual = datetime.now().strftime("%H:%M")
        respuesta = f"La hora actual es {hora_actual}."
        print("Respuesta de hora:", respuesta)
        return respuesta

    # Verificar si se pregunta por la fecha actual
    elif pregunta_limpia in ["que fecha es hoy", "dime la fecha", "que fecha es hoy?"]:
        fecha_actual = datetime.now().strftime("%d-%m-%Y")
        respuesta = f"La fecha de hoy es {fecha_actual}."
        print("Respuesta de fecha:", respuesta)
        return respuesta

    # Verificar si se pregunta por el día actual
    elif pregunta_limpia in ["que dia es hoy", "que dia estamos", "dime el dia"]:
        dia_actual = datetime.now().strftime("%A")
        dia_actual_espanol = dias_semana.get(dia_actual, "un día desconocido")
        respuesta = f"Hoy es {dia_actual_espanol}."
        print("Respuesta de día:", respuesta)
        return respuesta

    # Verificar si se pregunta por el año actual
    elif pregunta_limpia in ["que año es", "en que año estamos", "dime el año"]:
        anio_actual = datetime.now().strftime("%Y")
        respuesta = f"Estamos en el año {anio_actual}."
        print("Respuesta de año:", respuesta)
        return respuesta

    # Verificar si la pregunta por el presidente
    respuesta_presidente = presidente(pregunta_limpia, conocimientos)
    if respuesta_presidente != "Lo siento, no tengo información sobre ese presidente.":
        print("Respuesta sobre presidente:", respuesta_presidente)
        return respuesta_presidente

    # Verificar si se pregunta por signos zodiacales
    respuesta_signo = detectar_signo(pregunta_limpia)
    if respuesta_signo:
        print("Respuesta sobre signo:", respuesta_signo)
        return respuesta_signo

    # Verificar si la última pregunta fue para mostrar recetas, espera un número de elección
    if conocimientos["contexto"].get("ultimaPregunta") in ["receta", "recetas", "postres"]:
        try:
            num_receta = int(pregunta_limpia.strip())
            respuesta_receta = comida(pregunta_limpia, conocimientos, num_receta)
            print("Respuesta de elección de receta:", respuesta_receta)
            return respuesta_receta
        except ValueError:
            print("Error: No se ingresó un número para seleccionar una receta")
            return "Por favor, ingresa el número de la receta que deseas ver."

    # Verificar si el mensaje contiene las palabras clave "receta" o "postres"
    if "receta" in pregunta_limpia or "postres" in pregunta_limpia:
        respuesta_receta = comida(pregunta_limpia, conocimientos)
        print("Respuesta de lista de recetas:", respuesta_receta)
        return respuesta_receta

    # Verificar si la pregunta es una operación matemática
    respuesta_matematica = matematica(pregunta_limpia)
    if respuesta_matematica and "No pude entender la operación" not in respuesta_matematica:
        print("Respuesta matemática:", respuesta_matematica)
        return respuesta_matematica

    # Verificar si la consulta es sobre la huerta
    respuesta_huerta = huerta(pregunta_limpia, conocimientos)
    if respuesta_huerta and "No entendí tu solicitud" not in respuesta_huerta:
        print("Respuesta sobre huerta:", respuesta_huerta)
        return respuesta_huerta

    # Verificar si la pregunta es sobre geografía
    respuesta_geografia = geografia(pregunta_limpia, geografia_data)
    if respuesta_geografia:
        print("Respuesta de geografía:", respuesta_geografia)
        return respuesta_geografia

    # Verificar si la pregunta es sobre chistes
    respuesta_chiste = verificar_chiste(pregunta_limpia, conocimientos)
    if respuesta_chiste:
        print("Respuesta de verificación de chiste:", respuesta_chiste)
        return respuesta_chiste

    # Verificar primero si la pregunta menciona palabras clave de animales
    palabras_clave_animales = ["animal", "especie", "perro", "gato", "ave", "felino", "mamífero"]  # puedes expandir esta lista
    if any(palabra in pregunta_limpia for palabra in palabras_clave_animales):
        respuesta_animales = verificar_musica_animal(pregunta_limpia, conocimientos, animales_data)
        if respuesta_animales != "No tengo suficiente información para responder esta pregunta.":
            print("Respuesta sobre animales:", respuesta_animales)
            return respuesta_animales

    # Al final del flujo, si no hay respuesta específica
    respuesta_ia = entrenando_IA(pregunta_limpia, datos_previos, modo_administrador=es_administrador)
    if respuesta_ia:
        print(f"Respuesta generada por entrenando_IA: {respuesta_ia}")
        return respuesta_ia

    # Si no se encuentra ninguna respuesta, responde de manera amigable
    respuestas_amigables = [
        "¡Vaya! No estoy seguro de cómo responder a eso.",
        "Hmm, parece que no tengo una respuesta para eso.",
        "No estoy seguro de cómo ayudarte con eso.",
        "Esa es una gran pregunta.",
        "Parece que necesito un poco más de contexto."
    ]
    return random.choice(respuestas_amigables)

def verificar_procesar_mensaje(pregunta, conocimientos, animales_data, datos_previos, modo_administrador=False):
    # Limpiar y preparar la pregunta
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Paso 1: Buscar en conocimientos generales con similitud coseno
    respuestas_conocimientos = list(
        conocimientos.get("preguntas_respuestas", {}).values())
    claves_conocimientos = list(conocimientos.get(
        "preguntas_respuestas", {}).keys())
    similitudes_conocimientos = calcular_similitud_coseno(
        pregunta_limpia, claves_conocimientos)

    # Verificar si hay una coincidencia cercana en conocimientos generales
    if similitudes_conocimientos.size > 0 and similitudes_conocimientos.max() > UMBRAL_SIMILITUD:
        respuesta_seleccionada = respuestas_conocimientos[similitudes_conocimientos.argmax()]
        actualizar_historial(pregunta, respuesta_seleccionada, conocimientos, animales_data)
        return respuesta_seleccionada

    # Paso 2: Categoría específica - Buscar en animales_data
    subcategoria = None
    if "perro" in pregunta_limpia or "perros" in pregunta_limpia:
        subcategoria = "perro"
    elif "gato" in pregunta_limpia or "gatos" in pregunta_limpia or "felino" in pregunta_limpia:
        subcategoria = "gato"
    elif "ave" in pregunta_limpia or "pajaro" in pregunta_limpia:
        subcategoria = "ave"

    # Procesar animales_data si se encontró subcategoría
    if subcategoria:
        razas = animales_data.get("animal", {}).get(subcategoria, {})

        # Extraer los nombres de las razas para comparar con similitud coseno
        nombres_razas = list(razas.keys())
        similitudes_razas = calcular_similitud_coseno(pregunta_limpia, nombres_razas)

        # Verificar si hay una coincidencia cercana en las razas
        if similitudes_razas.size > 0 and similitudes_razas.max() > UMBRAL_SIMILITUD:
            raza_seleccionada = nombres_razas[similitudes_razas.argmax()]
            info = razas[raza_seleccionada]
            respuesta_raza = (f"{info['nombre_completo']}:<br><br>"
                              f"{info['descripcion']}<br><br>"
                              f"Características:<br><br>"
                              f"Peligro: {info['caracteristicas']['peligro']}<br>"
                              f"Docilidad: {info['caracteristicas']['docilidad']}<br>"
                              f"Amabilidad: {info['caracteristicas']['amabilidad']}<br>")
            return respuesta_raza

        # Respuesta en caso de que no se encuentre la raza específica en animales_data
        return {
            "perro": "Por el momento no he aprendido sobre ese perro.",
            "gato": "Por el momento no he aprendido sobre ese gato.",
            "ave": "Por el momento no he aprendido sobre ese ave."
        }.get(subcategoria, "Por favor, especifica una raza o especie.")

    # Al final del flujo, si no hay respuesta específica
    respuesta_ia = entrenando_IA(pregunta_limpia, datos_previos, modo_administrador=modo_administrador)
    if respuesta_ia:
        print(f"Respuesta generada por entrenando_IA: {respuesta_ia}")
        return respuesta_ia

    # Paso 4: Respuestas amigables si no se encuentra una respuesta
    respuestas_amigables = [
        "¡Vaya! No estoy seguro de cómo responder a eso. ¿Podrías reformular tu pregunta?",
        "Hmm, parece que no tengo una respuesta para eso.",
        "No estoy seguro de cómo ayudarte con eso.",
        "Esa es una gran pregunta. Déjame saber si tienes más detalles.",
        "Parece que necesito un poco más de contexto."
    ]
    return random.choice(respuestas_amigables)

