from funciones.funcion_eliminarAcentos import eliminar_acentos
import random, json

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


# Cargar conocimientos
conocimientos = cargar_datos('conocimientos.json')

def obtener_chiste(conocimientos):
    if "chiste" in conocimientos and "lista_chistes" in conocimientos["chiste"]:
        lista_chistes = conocimientos["chiste"]["lista_chistes"]
        return random.choice(lista_chistes)
    else:
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
