def huerta(consulta, conocimientos):
    # Verificar si el mensaje contiene "huerta", "plantas" o "verduras"
    if consulta.lower() in ["huerta", "plantas", "verduras"]:
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
    consulta_limpia = consulta.lower()
    if consulta_limpia in conocimientos.get("verduras", {}):
        verdura = conocimientos["verduras"][consulta_limpia]
        respuesta = (
            f"Nombre: {verdura['nombre']}<br>"
            f"• Temporada de siembra: {verdura['siembra']}<br>"
            f"• Temporada de cosecha: {verdura['cosecha']}<br>"
            f"• Frecuencia de riego: {verdura['riego']}<br>"
            f"• Tipo de tierra: {verdura['tierra']}"
        )
        return respuesta

    return "No entendí tu solicitud. Por favor, menciona 'huerta', 'plantas' o 'verduras' para obtener la lista, o el nombre de una verdura específica para más detalles."
