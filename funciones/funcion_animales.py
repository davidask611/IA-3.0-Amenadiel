import json
import random
from funciones.funcion_eliminarAcentos import eliminar_acentos
respuestas_amigables = [
    "¡Vaya! No estoy seguro de cómo responder a eso. ¿Podrías reformular tu pregunta?",
    "Hmm, parece que no tengo una respuesta para eso.",
    "No estoy seguro de cómo ayudarte con eso.",
    "Esa es una gran pregunta. Déjame saber si tienes más detalles.",
    "Parece que necesito un poco más de contexto."
]


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


def verificar_musica_animal(pregunta, conocimientos, animales_data):
    # Convertir la pregunta a minúsculas y eliminar acentos
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Iterar sobre las subcategorías de animales en el JSON
    for subcategoria in animales_data.get("animal", {}):
        # Verificar si el nombre de la subcategoría aparece en la pregunta
        if subcategoria in pregunta_limpia:
            razas = animales_data["animal"].get(subcategoria, {})

            # Revisar si la pregunta menciona una raza específica
            if any(raza in pregunta_limpia for raza in razas):
                # Buscar la raza específica en la pregunta y devolver detalles si se encuentra
                for raza, info in razas.items():
                    if raza in pregunta_limpia or info['nombre_completo'].lower() in pregunta_limpia:
                        return (f"{info['nombre_completo']}:<br><br>"
                                f"{info['descripcion']}<br><br>"
                                f"Características:<br><br>"
                                f"Peligro: {info['caracteristicas']['peligro']}<br>"
                                f"Docilidad: {info['caracteristicas']['docilidad']}<br>"
                                f"Amabilidad: {info['caracteristicas']['amabilidad']}<br>")

            # Respuesta genérica para la subcategoría sin raza específica
            return f"Por el momento no he aprendido sobre esa raza específica de {subcategoria}."

    # Verificar si la pregunta es sobre música (igual que antes)
    if "musica" in pregunta_limpia or "cantante" in pregunta_limpia or "informacion" in pregunta_limpia or \
       "canciones" in pregunta_limpia or "temas" in pregunta_limpia or "exitos" in pregunta_limpia or \
       "premios" in pregunta_limpia or "influencias" in pregunta_limpia:
        # [Código existente para la sección de música]
        # (reemplaza esta línea por el contenido que ya tienes en la sección de música)

        # Respuesta genérica si no se trata de animales ni de música
        return random.choice(respuestas_amigables)

    # Verificar si la pregunta es sobre música
    if "musica" in pregunta_limpia or "cantante" in pregunta_limpia or "informacion" in pregunta_limpia or "canciones" in pregunta_limpia or "temas" in pregunta_limpia or "exitos" in pregunta_limpia or "premios" in pregunta_limpia or "influencias" in pregunta_limpia:
        # Procesar la pregunta como una consulta sobre música
        musica = conocimientos.get("musica", {})
        palabras_pregunta = pregunta_limpia.split()

        # Lista de palabras clave para detectar las consultas
        palabras_cantante = ["musica", "cantante", "informacion"]
        palabras_canciones = ["canciones", "temas", "exitos"]
        palabras_premios = ["premios", "grammy", "golden globe", "mtv"]
        palabras_influencias = ["influencias"]

        nombre_detectado = None
        nombres_cantantes_json = [eliminar_acentos(
            nombre.lower()) for genero in musica.values() for nombre in genero.keys()]

        # Verificar si algún nombre de cantante en el JSON aparece en la pregunta
        for palabra in palabras_pregunta:
            if palabra in nombres_cantantes_json:
                nombre_detectado = palabra
                break

        # 1. Responder con la información completa de un cantante específico
        if "cantante" in pregunta_limpia and nombre_detectado:
            for genero, artistas in musica.items():
                for nombre_cantante, detalles in artistas.items():
                    nombre_cantante_limpio = eliminar_acentos(
                        nombre_cantante.lower())
                    if nombre_cantante_limpio == nombre_detectado:
                        # Devolver toda la información del cantante
                        respuesta = (f"{nombre_cantante}:<br>"
                                     f"Nombre completo: {detalles['nombre_completo']}<br>"
                                     f"Descripción: {detalles['descripcion']}<br>"
                                     f"Fecha de nacimiento: {detalles['fecha_nacimiento']}<br>"
                                     f"Nacionalidad: {detalles['nacionalidad']}<br><br>"
                                     f"Canciones más populares:<br>{'<br>'.join(detalles['canciones'])}<br><br>"
                                     f"Premios:<br>Grammy: {detalles['premios']['grammy']},<br>"
                                     f"Golden Globe: {detalles['premios']['golden_globe']},<br>"
                                     f"MTV Awards: {detalles['premios']['mtv_awards']}<br><br>"
                                     f"Influencias:<br>{', '.join(detalles['influencias'])}")
                        return respuesta

        # 2. Responder con una lista de todos los cantantes disponibles
        if "cantantes" in pregunta_limpia:
            if "conoces" in pregunta_limpia:
                # Devolver una lista de todos los cantantes sin importar el género
                lista_cantantes = [nombre_cantante.title(
                ) for genero in musica.values() for nombre_cantante in genero.keys()]
                return "Los cantantes que conozco son:<br>" + "<br>".join(lista_cantantes)

        # 3. Responder con una lista de cantantes por género
        if "cantantes de" in pregunta_limpia:
            # Detectar el género musical en la pregunta (pop, rock, reggaetón, etc.)
            generos_disponibles = musica.keys()
            for genero in generos_disponibles:
                if genero in pregunta_limpia:
                    # Devolver una lista de cantantes del género específico
                    lista_cantantes = [nombre_cantante.title()
                                       for nombre_cantante in musica[genero].keys()]
                    return f"Los cantantes de {genero} que conozco son:<br>" + "<br>".join(lista_cantantes)

        # Si no se detecta ninguna consulta válida
        return random.choice(respuestas_amigables)

    # Si la pregunta no está relacionada con música ni con animales
    return random.choice(respuestas_amigables)
