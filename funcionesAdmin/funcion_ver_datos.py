import os

def ver_datos(directorio_json='.'):
    archivos_json = [f for f in os.listdir(directorio_json) if f.endswith('.json')]
    if archivos_json:
        return {"respuesta": "Selecciona un archivo JSON para ver su contenido", "archivos": archivos_json}
    else:
        return {"respuesta": "No se encontraron archivos JSON en el directorio especificado."}
