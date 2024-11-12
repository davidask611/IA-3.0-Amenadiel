from funciones.funcion_eliminarAcentos import eliminar_acentos
import random


def obtener_chiste(conocimientos):
    try:
        lista_chistes = conocimientos["chiste"]["lista_chistes"]
        return random.choice(lista_chistes)
    except KeyError:
        return "Lo siento, no tengo chistes guardados."

# Función para verificar si se ha solicitado un chiste


def verificar_chiste(pregunta, conocimientos):
    # Convertir la pregunta a minúsculas y eliminar acentos
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Lista de palabras clave para identificar que se trata de un chiste
    palabras_clave_chiste = [
        "chiste", "cuentame un chiste", "otro chiste", "me cuentas un chiste"]

    # Verificar si alguna de las palabras clave está en la pregunta
    if any(palabra in pregunta_limpia for palabra in palabras_clave_chiste):
        return obtener_chiste(conocimientos)

    return None  # Retornar None si no es una pregunta sobre chistes
