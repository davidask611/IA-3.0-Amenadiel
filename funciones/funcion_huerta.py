from funciones.funcion_eliminarAcentos import eliminar_acentos

def huerta(pregunta_limpia, conocimientos):
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())
    # Verificar si el mensaje contiene "huerta", "plantas" o "verduras"
    if pregunta_limpia.lower() in ["huerta", "plantas", "verduras"]:
        # Obtener lista de verduras disponibles
        verduras_data = conocimientos.get("verduras", {})
        if not verduras_data:
            return "No hay información disponible sobre las verduras en el recetario."

        lista_verduras = "<br>".join(
            [f"{i + 1}. {v.capitalize()}" for i, v in enumerate(verduras_data.keys())])
        respuesta = f"Verduras disponibles:<br>{lista_verduras}"
        respuesta += "<br><br>Escribe un nombre para obtener mas detalles."
        return respuesta

    # Si el mensaje coincide con el nombre de una verdura específica
    pregunta_limpia = pregunta_limpia.lower()
    if pregunta_limpia in conocimientos.get("verduras", {}):
        verdura = conocimientos["verduras"][pregunta_limpia]
        respuesta = (
            f"Nombre: {verdura['nombre']}<br>"
            f"• Temporada de siembra: {verdura['siembra']}<br>"
            f"• Temporada de cosecha: {verdura['cosecha']}<br>"
            f"• Frecuencia de riego: {verdura['riego']}<br>"
            f"• Tipo de tierra: {verdura['tierra']}"
        )
        return respuesta

    return "No entendí tu solicitud. Por favor, menciona 'huerta', 'plantas' o 'verduras' para obtener la lista, o el nombre de una verdura específica para más detalles."
