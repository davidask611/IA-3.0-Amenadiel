import json
from flask import Flask, render_template, request, jsonify, session
from Amenadiel import procesar_mensaje, ver_datos as obtener_datos, conocimientos, geografia_data, matematica, animales_data, comida
import pdfplumber
from funcionesAdmin.manejo_archivos import process_json, process_txt, process_pdf
from werkzeug.utils import secure_filename
from funcionesAdmin.funcion_aprender import entrenando_IA, datos_previos
from funciones.funcion_eliminarAcentos import eliminar_acentos
from funciones.funcion_geografia import geografia
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from funciones.funcion_comida import comida

app = Flask(__name__)

# Configuración de clave secreta para la sesión
app.secret_key = 'clave_secreta'  # Asegúrate de que sea única y segura
# app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB para todos

@app.route("/", methods=["GET"])
def home():
    session['modo_administrador'] = False  # Restablecer a False en cada carga
    return render_template("index.html")

# Endpoint para ver datos
@app.route("/ver_datos", methods=["POST"])
def ver_datos():
    if not session.get('modo_administrador', False):
        print("Intento de acceso sin privilegios de administrador")
        return jsonify({"respuesta": "No tienes acceso para ver los datos."})

    # Obtener lista de archivos JSON en el directorio
    directorio_json = '.'  # Cambiar a la ruta que desees
    archivos_json = [f for f in os.listdir(
        directorio_json) if f.endswith('.json')]

    if archivos_json:
        # Crear una lista numerada de archivos JSON
        lista_archivos = "\n".join(
            [f"{i+1}. {archivo}" for i, archivo in enumerate(archivos_json)])
        respuesta = f"Selecciona un archivo JSON para ver su contenido:\n{lista_archivos}"
        print(f"Archivos JSON encontrados: {archivos_json}")
        return jsonify({"respuesta": respuesta, "archivos": archivos_json})
    else:
        print("No se encontraron archivos JSON en el directorio.")
        return jsonify({"respuesta": "No se encontraron archivos JSON en el directorio."})


@app.route("/ver_contenido", methods=["POST"])
def ver_contenido():
    if not session.get('modo_administrador', False):
        return jsonify({"respuesta": "No tienes acceso para ver los datos."})

    # Obtener el nombre del archivo seleccionado
    archivo_seleccionado = request.json.get("archivo")

    if not archivo_seleccionado:
        return jsonify({"respuesta": "No se especificó un archivo."})

    # Verificar si el archivo existe
    if not os.path.isfile(archivo_seleccionado):
        return jsonify({"respuesta": f"El archivo {archivo_seleccionado} no existe."})

    # Leer el contenido del archivo JSON
    try:
        with open(archivo_seleccionado, "r", encoding="utf-8") as f:
            contenido = json.load(f)
        return jsonify({"respuesta": f"Contenido de {archivo_seleccionado}: {json.dumps(contenido, indent=2)}"})
    except Exception as e:
        return jsonify({"respuesta": f"Error al leer el archivo: {str(e)}"})

# carga y proceso de archivos

UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ruta para manejar la subida de archivos
@app.route("/subir_archivo", methods=["POST"])
def subir_archivo():
    archivo = request.files.get("archivo")
    es_administrador = session.get('modo_administrador', False)
    max_file_size = 10 * 1024 * 1024  # 10 MB

    # Verificar si el archivo excede el límite de tamaño (solo para usuarios no administradores)
    if not es_administrador and archivo.content_length > max_file_size:
        return jsonify({"error": "El archivo es demasiado grande. Solo se permiten archivos de hasta 10 MB para usuarios."}), 400

    # Guardar el archivo en la carpeta uploads
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(archivo.filename))
    archivo.save(file_path)

    # Procesar el archivo dependiendo del tipo y obtener su contenido
    if archivo.filename.endswith(".json"):
        contenido = process_json(file_path)
    elif archivo.filename.endswith(".txt"):
        contenido = process_txt(file_path)
    elif archivo.filename.endswith(".pdf"):
        contenido = process_pdf(file_path)
    else:
        return jsonify({"error": "Tipo de archivo no soportado. Solo se admiten archivos JSON, TXT y PDF."}), 400

    # Enviar el contenido al chat (o un mensaje de error si algo salió mal)
    if not contenido:
        return jsonify({"respuesta": "No se pudo leer el contenido del archivo."}), 400

    # Respuesta para mostrar en el chat
    return jsonify({"respuesta": contenido})

@app.route("/chat", methods=["POST"])
def chat():
    # Obtener el mensaje y el estado del administrador
    pregunta_limpia = request.json.get("mensaje")
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())
    es_administrador = request.json.get("es_administrador", False)

    # Activar modo administrador en la sesión si corresponde
    if es_administrador:
        session['modo_administrador'] = True
        print("Modo administrador activado en sesión.")

    print(f"Mensaje recibido en Flask: '{pregunta_limpia}'")
    print(f"Estado de administrador: {session.get('modo_administrador', False)}")

    # Verificar si la última pregunta fue para mostrar recetas y si se recibe un número de elección
    if conocimientos["contexto"].get("ultimaPregunta") in ["receta", "recetas", "postres"]:
        try:
            # Intentar convertir la respuesta a número para seleccionar la receta
            num_receta = int(pregunta_limpia.strip())
            respuesta_receta = comida(pregunta_limpia, conocimientos, num_receta)
            conocimientos["contexto"]["ultimaPregunta"] = None  # Limpiar contexto
            print("Respuesta de elección de receta:", respuesta_receta)
            return jsonify({"respuesta": respuesta_receta})
        except ValueError:
            # Mensaje para el caso en que no se ingrese un número válido
            print("Error: No se ingresó un número para seleccionar una receta")
            return jsonify({"respuesta": "Por favor, ingresa el número de la receta que deseas ver."})

    # Verificar si el mensaje contiene las palabras clave "receta" o "postres"
    if "receta" in pregunta_limpia or "postres" in pregunta_limpia:
        conocimientos["contexto"]["ultimaPregunta"] = "receta"
        respuesta_receta = comida(pregunta_limpia, conocimientos)
        print("Respuesta de lista de recetas:", respuesta_receta)
        return jsonify({"respuesta": respuesta_receta})

    # Primero, procesamos el mensaje con la función de matemáticas
    respuesta_matematica = matematica(pregunta_limpia.lower())
    if respuesta_matematica and "No pude entender la operación" not in respuesta_matematica:
        print(f"Resultado matemático procesado: {respuesta_matematica}")
        return jsonify({"respuesta": respuesta_matematica})

    # Si está en modo administrador, intentamos buscar respuesta en `entrenando_IA`
    if session.get('modo_administrador', False):
        respuesta_ia = entrenando_IA(pregunta_limpia, datos_previos, modo_administrador=True)
        if respuesta_ia:
            print(f"Respuesta generada por entrenando_IA: {respuesta_ia}")
            return jsonify({"respuesta": respuesta_ia})

    # Si no es una operación matemática y no se encontró en `entrenando_IA`, procesar el mensaje normalmente
    respuesta = procesar_mensaje(pregunta_limpia, conocimientos, geografia_data, animales_data, datos_previos, es_administrador=session.get('modo_administrador', False))
    print(f"Respuesta generada: {respuesta}")
    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    app.run(debug=True)
