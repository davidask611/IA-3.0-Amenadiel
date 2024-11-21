import os
import json


def ver_datos(directorio_json='.', archivo_seleccionado=None):
    # Lista de archivos JSON en el directorio
    archivos_json = [f for f in os.listdir(
        directorio_json) if f.endswith('.json')]

    if archivo_seleccionado:  # Si se seleccionó un archivo
        ruta_archivo = os.path.join(directorio_json, archivo_seleccionado)
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                contenido = json.load(archivo)  # Cargar contenido JSON
            return {"respuesta": "Contenido del archivo seleccionado", "contenido": contenido}
        else:
            return {"respuesta": "El archivo seleccionado no existe."}

    if archivos_json:  # Lista de archivos JSON disponibles
        return {"respuesta": "Selecciona un archivo JSON para ver su contenido", "archivos": archivos_json}
    else:
        return {"respuesta": "No se encontraron archivos JSON en el directorio especificado."}
