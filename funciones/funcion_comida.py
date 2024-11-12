def comida(consulta, conocimientos, num_receta=None):
    # Detectar palabras clave para mostrar la lista de recetas
    if "recetas" in consulta.lower() or "receta" in consulta.lower() or "postres" in consulta.lower() or "postre" in consulta.lower():
        recetas = list(conocimientos.get("recetario", {}).keys())
        if recetas:
            if num_receta is None:
                # Si no se ha dado un número, mostrar la lista de recetas
                respuesta = "Recetas disponibles:<br>"
                respuesta += "<br>".join([f"{idx}. {receta}" for idx, receta in enumerate(recetas, start=1)])
                respuesta += "<br>Elige el número de la receta que quieres ver."
                return respuesta
            else:
                # Si se ha dado un número, mostrar la receta seleccionada
                if 1 <= num_receta <= len(recetas):
                    nombre_comida = recetas[num_receta - 1]
                    receta = conocimientos["recetario"][nombre_comida]

                    detalles = f"Receta de {nombre_comida}:<br><br><br>"
                    detalles += "Ingredientes: <br>"
                    detalles += "<br>".join([f"- {ingrediente}" for ingrediente in receta['ingredientes']])
                    detalles += "<br><br>Paso a paso:<br>"
                    detalles += "<br>".join([f"-> {paso}" for paso in receta['paso_a_paso']])
                    return detalles
                else:
                    return "Número fuera de rango. Inténtalo nuevamente."
        else:
            return "No hay recetas disponibles en el recetario."
    else:
        return "No entendí tu solicitud. Si quieres ver las recetas, usa una consulta que incluya 'receta', 'recetas' o 'postres'."
