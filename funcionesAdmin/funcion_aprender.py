import os
import json
from difflib import get_close_matches

def entrenando_IA(pregunta, datos_previos, modo_administrador=False):
    """
    Función que busca una respuesta en los datos_previos para una pregunta específica.
    Sigue un flujo diferente para usuario y administrador.
    
    Parámetros:
    - pregunta (str): La pregunta realizada por el usuario o administrador.
    - datos_previos (dict): Los datos de entrenamiento y público en los que se buscarán las respuestas.
    - modo_administrador (bool): Si True, aplica el flujo de administrador.
    
    Retorno:
    - str: Respuesta generada en base a los datos disponibles o un mensaje para aprender.
    """
    
    # Prepara la búsqueda en 'entrenamiento' o 'publico' según el rol
    seccion_primaria = "entrenamiento" if modo_administrador else "publico"
    seccion_secundaria = "publico" if modo_administrador else "entrenamiento"
    
    # Inicializa intentos si es modo administrador
    intentos_restantes = 3 if modo_administrador else 1
    
    # Definir función para búsqueda en sección específica
    def buscar_en_seccion(seccion):
        resultados = []
        for categoria, contenido in datos_previos.get(seccion, {}).items():
            if isinstance(contenido, dict):  # Si es una sección de "publico"
                # Busca coincidencias exactas o aproximadas
                respuesta_exacta = contenido.get(pregunta)
                if respuesta_exacta:
                    return [respuesta_exacta]  # Respuesta exacta encontrada
                
                # Buscar mejor coincidencia usando difflib
                mejor_coincidencia = get_close_matches(pregunta.lower(), contenido.keys(), n=1, cutoff=0.6)
                if mejor_coincidencia:
                    resultados.append(contenido[mejor_coincidencia[0]])
            elif isinstance(contenido, list):  # Si es una sección de "entrenamiento"
                # Busca coincidencias exactas en la lista de entrenamiento
                for frase in contenido:
                    if pregunta.lower() in frase.lower():
                        resultados.append(frase)
        return resultados

    # Flujo de búsqueda para usuario y administrador
    while intentos_restantes > 0:
        # Busca en la sección primaria (entrenamiento o publico según el rol)
        resultados = buscar_en_seccion(seccion_primaria)
        if resultados:
            return f"Respuesta encontrada en {seccion_primaria.capitalize()}: {resultados[0]}"

        # Si no encontró en la sección primaria, intenta en la secundaria
        resultados = buscar_en_seccion(seccion_secundaria)
        if resultados:
            return f"Respuesta encontrada en {seccion_secundaria.capitalize()}: {resultados[0]}"
        
        # Si modo administrador y no encuentra respuesta válida en ambos secciones
        if modo_administrador:
            print(f"Intento {4 - intentos_restantes}/3 para generar respuesta...")
            respuesta_generada = generar_respuesta_por_similitud(pregunta)  # Llamar a función de similitud (usar embeddings, etc.)
            confirmacion = input(f"Respuesta sugerida: {respuesta_generada}\n¿Es coherente? (si/no): ")
            if confirmacion.lower() == "si":
                mostrar_categorias(datos_previos["publico"])  # Muestra categorías para guardar la respuesta
                return f"Respuesta confirmada: {respuesta_generada}"
            intentos_restantes -= 1

        # Si no es administrador o agota los intentos
        if not modo_administrador or intentos_restantes == 0:
            return "No encontré una respuesta. Por favor, enséñame la respuesta correcta."

    return "No se ha encontrado información relacionada."

def generar_respuesta_por_similitud(pregunta):
    """
    Genera una respuesta por similitud usando una técnica como embeddings o TF-IDF.
    """
    # Placeholder para técnica avanzada, usa TF-IDF o embeddings (ej. Spacy o transformers)
    return "Respuesta generada por similitud (demo)"

def mostrar_categorias(publico):
    """
    Muestra categorías disponibles para agregar una nueva respuesta confirmada.
    """
    print("Elige una categoría para guardar la respuesta o crea una nueva:")
    for categoria in publico.keys():
        print(f"- {categoria}")
    print("- Nueva categoría")
