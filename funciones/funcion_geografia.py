from funciones.funcion_eliminarAcentos import eliminar_acentos
# Función para manejar las consultas sobre geografía


def geografia(pregunta_limpia, geografia_data):
    """
    Procesa una consulta de geografía y devuelve la información solicitada.
    Permite consultar sobre temas específicos: país, provincias y cultura.
    Si el usuario escribe "historia argentina", "información de argentina" o
    "información del pais", se le ofrecen opciones de consulta.
    """
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())

    # Paso 1: Ofrece opciones al usuario si la consulta es general
    if pregunta_limpia in [
        "historia argentina",
        "información de argentina",
        "información del pais",
    ]:
        opciones = ["pais", "provincias", "cultura"]
        respuesta = "Aquí tienes información sobre otros temas:<br>"
        respuesta += "Opciones disponibles:<br>"
        respuesta += "<br>".join(
            [
                f"{idx + 1}. {opcion.capitalize()
                              }"
                for idx, opcion in enumerate(opciones)
            ]
        )
        respuesta += "<br><br>Escribe una opción para más detalles (ejemplo: pais, provincias, cultura)."
        return respuesta

    # Paso 2: Procesa la opción elegida por el usuario
    if pregunta_limpia == "pais":
        # Devuelve detalles del país si el usuario elige "pais"
        pais = geografia_data.get("pais", {})
        respuesta = (
            f"Información del país:<br>"
            f"a. País: {pais.get('nombre', 'Desconocido')}<br>"
            f"b. Países limítrofes: {
                ', '.join(pais.get('paisesLimitrofes', []))}<br>"
            f"c. Moneda oficial: {
                pais.get('monedaOficial', 'Desconocido')}<br>"
            f"d. Presidente actual: {
                pais.get('presidenteActual', 'Desconocido')}<br>"
        )
        return respuesta

    elif pregunta_limpia == "provincias":
        # Devuelve la lista de provincias y sus capitales si el usuario elige "provincias"
        provincias = geografia_data.get("provincias", [])
        if provincias:
            respuesta = "Lista de provincias y sus capitales:<br>"
            respuesta += "<br>".join(
                [
                    f"{idx + 1}. Provincia: {prov['provincia']}, Capital: {
                        prov['capital']}"
                    for idx, prov in enumerate(provincias)
                ]
            )
            return respuesta
        else:
            return "No hay información disponible sobre las provincias."

    elif pregunta_limpia == "cultura":
        # Devuelve información cultural si el usuario elige "cultura"
        cultura = geografia_data.get("cultura", {})
        respuesta = (
            f"Música Popular: {
                ', '.join(cultura.get('musicaPopular', []))}<br>"
            f"Museos Importantes: {
                ', '.join(cultura.get('museosImportantes', []))}<br>"
            f"Comidas Típicas: {
                ', '.join(cultura.get('comidasTipicas', []))}<br>"
        )
        return respuesta

    # Devuelve `None` si la consulta no coincide con ninguna opción válida
    return None
