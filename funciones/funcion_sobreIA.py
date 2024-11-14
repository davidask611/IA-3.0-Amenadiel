from funciones.funcion_eliminarAcentos import eliminar_acentos

# Función para responder sobre la IA
def responder_sobre_ia(pregunta_limpia, conocimientos):
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())
    if pregunta_limpia in conocimientos["datosdelaIA"]:
        return conocimientos["datosdelaIA"][pregunta_limpia]
    return None  # Si la pregunta no está en el JSON, devolvemos None
