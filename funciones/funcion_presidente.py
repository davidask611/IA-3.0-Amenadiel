import re
import datetime
from funciones.funcion_eliminarAcentos import eliminar_acentos
# Función para responder sobre presidente


def presidente(pregunta, conocimientos):
    # Convertir la pregunta a minúsculas sin acentos
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Dividir la pregunta en palabras
    palabras_pregunta = pregunta_limpia.split()

    # Lista de presidentes en el diccionario
    presidentes = conocimientos.get("presidente", {})

    # Verificar si la pregunta contiene la palabra "presidente"
    if "presidente" in palabras_pregunta or "fue" in palabras_pregunta or "era" in palabras_pregunta:
        # Buscar si hay un año en la pregunta
        # Buscar un año de 4 cifras
        anio_encontrado = re.search(r"\b\d{4}\b", pregunta_limpia)

        # Si se encuentra un año de 4 cifras
        if anio_encontrado:
            anio = int(anio_encontrado.group())

            # Recorrer todos los presidentes para verificar su periodo
            for nombre_presidente, detalles in presidentes.items():
                periodo = detalles['periodo'].split(' - ')
                anio_inicio = int(periodo[0])
                anio_fin = int(
                    periodo[1]) if periodo[1] != "presente" else datetime.now().year

                # Verificar si el año está dentro del periodo del presidente
                if anio_inicio <= anio <= anio_fin:
                    return (f"{detalles['nombre_completo']} fue presidente entre {detalles['periodo']}.")

            # Si no se encuentra un presidente para ese año
            return f"No tengo información sobre quién fue presidente en el año {anio}. Intenta con 'quién fue presidente en el año 2022'."

        # Verificar si se encuentra un año de solo dos cifras
        anio_dos_cifras = re.search(r"\b\d{2}\b", pregunta_limpia)
        if anio_dos_cifras:
            return "No tengo información sobre ese presidente o esa fecha. Por favor, intenta con un año de cuatro cifras, como 'quién fue presidente en el año 2022'."

        # Si no se encontró un año, buscar por el nombre del presidente
        for nombre_presidente, detalles in presidentes.items():
            # Limpiar el nombre del presidente para compararlo con la pregunta
            nombre_presidente_limpio = eliminar_acentos(
                nombre_presidente.lower())

            # Verificar si el nombre del presidente está en la pregunta
            if nombre_presidente_limpio in palabras_pregunta:
                return (f"{detalles['nombre_completo']} fue presidente entre {detalles['periodo']}. "
                        f"Descripción: {detalles['descripcion']}")

    return "Lo siento, no tengo información sobre ese presidente."
