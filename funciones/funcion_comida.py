from funciones.funcion_eliminarAcentos import eliminar_acentos

def comida(pregunta, conocimientos, num_receta=None):
    pregunta_limpia = eliminar_acentos(pregunta.lower())
    recetas = list(conocimientos.get("recetario", {}).keys())

    # Si el usuario ingresó un número, intentar usarlo para mostrar la receta
    if num_receta is not None:
        if 1 <= num_receta <= len(recetas):
            nombre_comida = recetas[num_receta - 1]
            receta = conocimientos["recetario"][nombre_comida]
            detalles = f"Receta de {nombre_comida}:<br><br>"
            detalles += "Ingredientes: <br>"
            detalles += "<br>".join([f"- {ingrediente}" for ingrediente in receta['ingredientes']])
            detalles += "<br><br>Paso a paso:<br>"
            detalles += "<br>".join([f"-> {paso}" for paso in receta['paso_a_paso']])
            return detalles
        else:
            return "Número fuera de rango. Inténtalo nuevamente."

    # Si el usuario pidió por nombre, verificar si el nombre de la receta coincide
    elif any(word in pregunta_limpia for word in ["recetas", "receta", "postres"]):
        if not num_receta:
            respuesta = "Recetas disponibles:<br>"
            respuesta += "<br>".join([f"{idx}. {receta}" for idx, receta in enumerate(recetas, start=1)])
            respuesta += "<br>Elige el número o nombre de la receta que quieres ver."
            return respuesta
        else:
            for receta in recetas:
                if pregunta_limpia in receta.lower():
                    receta_detalles = conocimientos["recetario"][receta]
                    detalles = f"Receta de {receta}:<br><br>"
                    detalles += "Ingredientes: <br>"
                    detalles += "<br>".join([f"- {ingrediente}" for ingrediente in receta_detalles['ingredientes']])
                    detalles += "<br><br>Paso a paso:<br>"
                    detalles += "<br>".join([f"-> {paso}" for paso in receta_detalles['paso_a_paso']])
                    return detalles
            return "No encontré ninguna receta que coincida con el nombre proporcionado."
    else:
        return "No entendí tu solicitud. Usa palabras como 'receta' o 'postre' para ver opciones."

