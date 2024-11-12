import re
import json
from funciones.funcion_eliminarAcentos import eliminar_acentos


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


conocimientos = cargar_datos()
# Asegurarse de que los signos están en el diccionario 'conocimientos'
signos_zodiacales = conocimientos.get("signos_zodiacales", {})

# Función para obtener la descripción de un signo zodiacal desde el diccionario cargado


def obtener_signo(signo):
    # Convertimos a minúsculas para evitar errores de mayúsculas/minúsculas
    signo = signo.lower()
    if signo in signos_zodiacales:
        # Construir la respuesta con la descripción y más detalles del signo
        info_signo = signos_zodiacales[signo]
        # Convertir lista a cadena
        compatibilidad = ", ".join(info_signo['compatibilidad'])
        descripcion = (f"El signo {signo.capitalize()} cubre desde {info_signo['fecha-fecha']}. "
                       f"Su elemento es {info_signo['elemento']}. {
                           info_signo['descripcion']} "
                       f"Es compatible con: {compatibilidad}.")
        return descripcion
    else:
        return "Lo siento, no tengo información sobre ese signo."

# Función para detectar signos zodiacales con 're'


def detectar_signo(pregunta):
    # Eliminar acentos y convertir a minúsculas
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Crear un patrón que busque signos zodiacales
    # Crear un patrón para todos los signos (ej. 'aries|tauro|geminis')
    signos = '|'.join(signos_zodiacales.keys())
    # Solo buscar signos, sin necesidad de "signo" antes o después
    patron = rf"\b({signos})\b"

    # Buscar el patrón en la pregunta
    coincidencia = re.search(patron, pregunta_limpia)

    if coincidencia:
        # Si se encuentra un signo en la pregunta, devolver la información del signo
        signo_encontrado = coincidencia.group(1)
        return obtener_signo(signo_encontrado)

    return None  # Si no se encuentra ninguna coincidencia
