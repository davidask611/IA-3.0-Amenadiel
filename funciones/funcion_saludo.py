from funciones.funcion_eliminarAcentos import eliminar_acentos
# Función para buscar un saludo
def buscar_saludo(pregunta_limpia, conocimientos):
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())
    # Obtener la lista de saludos del archivo JSON
    saludos = conocimientos.get("saludos", {})

    # Intentar encontrar un saludo exacto
    for saludo in saludos:
        if saludo in pregunta_limpia:
            return saludos[saludo]

    # Si no encuentra el saludo, puedes intentar buscar coincidencias parciales
    # Divide la pregunta en palabras
    palabras_pregunta = set(pregunta_limpia.split())
    for saludo, respuesta in saludos.items():
        palabras_saludo = set(saludo.split())  # Divide los saludos en palabras

        # Verifica si alguna palabra del saludo coincide con la pregunta
        if palabras_saludo & palabras_pregunta:  # El operador & busca intersección
            return respuesta

    return None