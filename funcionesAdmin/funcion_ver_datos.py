import os


def ver_datos(directorio_json='.'):
    print(f"Directorio JSON utilizado: {directorio_json}")
    archivos_json = [f for f in os.listdir(
        directorio_json) if f.endswith('.json')]

    print(f"Archivos JSON encontrados: {archivos_json}")
    if not archivos_json:
        return "No se encontraron archivos JSON en el directorio especificado."
