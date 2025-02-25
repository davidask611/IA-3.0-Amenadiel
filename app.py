# import datetime
from config import Config
import json
import mimetypes
from flask import Flask, render_template, request, jsonify
from Amenadiel import procesar_mensaje, conocimientos, geografia_data, matematica, animales_data, comida
from funcionesAdmin.manejo_archivos import process_json, process_txt, process_pdf
from werkzeug.utils import secure_filename
from funcionesAdmin.funcion_aprender import entrenando_IA, datos_previos, guardar_datos, generar_respuesta_por_similitud, buscar_en_archivos_uploads
from funciones.funcion_eliminarAcentos import eliminar_acentos
import sys
import os
import time
from flask import session

# from datetime import timedelta
from registro_acciones import registrar_accion
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Configuración de la clave secreta para la sesión y parámetros
app.config.from_object(Config)

# Configuración para la sesión
app.secret_key = Config.SECRET_KEY
app.config['SESSION_PERMANENT'] = True


# # Función para registrar acciones en un archivo de log


@app.route("/registrar_accion", methods=["POST"])
def registrar_accion_api():
    """
    Endpoint para registrar una acción desde el frontend.
    """
    accion = request.json.get("accion")
    if not accion:
        return jsonify({"respuesta": "No se proporcionó ninguna acción para registrar."}), 400

    try:
        registrar_accion(accion)
        return jsonify({"respuesta": "Acción registrada correctamente."}), 200
    except Exception as e:
        return jsonify({"respuesta": f"Error al registrar la acción: {str(e)}"}), 500


# Función para limpiar archivos obsoletos (más de 60 días)

def limpiar_archivos_obsoletos():
    # Verificar si la carpeta de subida existe
    upload_folder = app.config.get('UPLOAD_FOLDER', './uploads')
    if not os.path.exists(upload_folder):
        registrar_accion(f"La carpeta {upload_folder} no existe.")
        return

    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        if os.path.isfile(file_path):
            file_age = time.time() - os.path.getmtime(file_path)
            if file_age > 60 * 24 * 60 * 60:  # Más de 60 días
                try:
                    os.remove(file_path)
                    registrar_accion(f"Archivo eliminado: {file_path}")
                except OSError as e:
                    registrar_accion(f"Error eliminando {file_path}: {str(e)}")


# Ruta principal
@app.route("/", methods=["GET"])
def home():
    if 'modo_administrador' not in session:
        session['modo_administrador'] = False
        # limpiar_archivos_obsoletos()  # Limpia archivos obsoletos al cargar la página principal
    return render_template("index.html")


@app.route("/subir_archivo", methods=["POST"])
def subir_archivo():
    archivo = request.files.get("archivo")
    modo_administrador = session.get('modo_administrador', False)

    if not archivo:
        registrar_accion("No se recibió ningún archivo.")
        return jsonify({"error": "No se recibió ningún archivo."}), 400

    # Validar tamaño del archivo (solo para usuarios)
    if not modo_administrador and archivo.content_length > 5 * 1024 * 1024:  # 5 MB
        return jsonify({"error": "El archivo es demasiado grande. Solo se permiten archivos de hasta 5 MB para usuarios."}), 400

    # Validar tipo MIME
    mime_type, _ = mimetypes.guess_type(archivo.filename)
    allowed_mime_types = ["application/json", "text/plain", "application/pdf"]
    if mime_type not in allowed_mime_types:
        registrar_accion("Tipo de archivo no permitido.")
        return jsonify({"error": "Tipo de archivo no permitido."}), 400

    # Guardar archivo en 'uploads'
    upload_folder = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, secure_filename(archivo.filename))

    # Evitar reprocesamiento si el archivo ya existe
    if os.path.exists(file_path):
        registrar_accion(f"El archivo ya existe y no será reprocesado: {file_path}")
        return jsonify({"respuesta": "El archivo ya fue subido anteriormente."}), 200

    archivo.save(file_path)
    registrar_accion(f"Archivo guardado exitosamente en: {file_path}")

    # Procesar el archivo según su extensión
    if archivo.filename.endswith(".json"):
        contenido = process_json(file_path)
    elif archivo.filename.endswith(".txt"):
        contenido = process_txt(file_path)
    elif archivo.filename.endswith(".pdf"):
        contenido = process_pdf(file_path)
    else:
        return jsonify({"error": "Tipo de archivo no soportado. Solo JSON, TXT y PDF."}), 400

    # Respuesta final
    if not contenido:
        return jsonify({"respuesta": "No se pudo leer el contenido del archivo."}), 400

    return jsonify({"respuesta": contenido})



# Endpoint para ver datos
@app.route("/ver_datos", methods=["POST"])
def ver_datos():
    if not session.get('modo_administrador', False):
        return jsonify({"respuesta": "No tienes acceso para ver los datos."})

    # Buscar archivos JSON en la raíz del proyecto
    directorio_json = '.'  # Raíz del proyecto
    archivos_json = [f for f in os.listdir(
        directorio_json) if f.endswith('.json')]

    if archivos_json:
        lista_archivos = "\n".join(
            [f"{i+1}. {archivo}" for i, archivo in enumerate(archivos_json)]
        )
        respuesta = f"Selecciona un archivo JSON para ver su contenido:\n{lista_archivos}"
        return jsonify({"respuesta": respuesta, "archivos": archivos_json})
    else:
        return jsonify({"respuesta": "No se encontraron archivos JSON en el directorio."})


# Endpoint para ver contenido de un archivo JSON
@app.route("/ver_contenido", methods=["POST"])
def ver_contenido():
    # Verificar si el usuario tiene permisos de administrador
    if not session.get('modo_administrador', False):
        return jsonify({"respuesta": "No tienes acceso para ver los datos."})

    # Obtener el nombre del archivo desde el JSON enviado
    archivo_seleccionado = request.json.get("archivo")
    if not archivo_seleccionado:
        return jsonify({"respuesta": "No se especificó un archivo."})

    # Sanitizar el nombre del archivo para evitar vulnerabilidades
    archivo_seleccionado = secure_filename(archivo_seleccionado)
    ruta_archivo = os.path.join('.', archivo_seleccionado)  # Raíz del proyecto

    # Verificar si el archivo existe
    if not os.path.isfile(ruta_archivo):
        return jsonify({"respuesta": f"El archivo {archivo_seleccionado} no existe."})

    # Leer el contenido del archivo JSON seleccionado
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = json.load(f)  # Convertir JSON a diccionario
        return jsonify({
            "respuesta": f"Contenido del archivo {archivo_seleccionado}:",
            "contenido": contenido  # Enviar contenido del archivo
        })
    except json.JSONDecodeError as e:
        return jsonify({"respuesta": f"El archivo {archivo_seleccionado} no contiene un JSON válido. Error: {str(e)}"})
    except Exception as e:
        return jsonify({"respuesta": f"Error al leer el archivo: {str(e)}"})


# Datos en memoria simulando `entrenando_IA`
estado_confirmacion = {}


# Confirmación de respuesta
@app.route("/confirmar_respuesta", methods=["POST"])
def confirmar_respuesta():
    global estado_confirmacion
    if not estado_confirmacion.get("confirmacion_pendiente"):
        registrar_accion("Intento de confirmar sin confirmación pendiente")
        return jsonify({"respuesta": "No hay confirmaciones pendientes."}), 400

    data = request.json
    categoria = data.get("categoria")
    registrar_accion(f"Confirmación recibida para categoría: {categoria}")

    categorias_disponibles = estado_confirmacion.get("categorias", [])
    if not categoria or categoria not in categorias_disponibles:
        registrar_accion(f"Categoría inválida seleccionada: {categoria}")
        return jsonify({
            "respuesta": f"Por favor, selecciona una categoría válida: {', '.join(categorias_disponibles)}"
        }), 400

    # Guardar la respuesta en la categoría seleccionada
    pregunta = estado_confirmacion["pregunta"]
    respuesta = estado_confirmacion["respuesta"]
    datos_previos["publico"].setdefault(categoria, {})[pregunta] = respuesta
    guardar_datos(datos_previos)  # Guardar datos actualizados
    registrar_accion(
        f"Respuesta guardada en la categoría '{categoria}' para la pregunta '{pregunta}'")

    estado_confirmacion.clear()
    return jsonify({"respuesta": f"La respuesta se guardó correctamente en la categoría '{categoria}'."}), 200


@app.route("/rechazar_respuesta", methods=["POST"])
def rechazar_respuesta():
    """
    Maneja el rechazo de una respuesta confirmada.
    Registra la acción y devuelve un mensaje correspondiente.
    """
    global estado_confirmacion

    if not estado_confirmacion.get("confirmacion_pendiente"):
        registrar_accion("Intento de rechazo sin confirmación pendiente")
        return jsonify({"respuesta": "No hay confirmaciones pendientes."}), 400

    # Limpiar estado de confirmación
    estado_confirmacion.clear()
    registrar_accion("Respuesta rechazada correctamente")

    return jsonify({"respuesta": "La respuesta fue rechazada."}), 200


estado_confirmacion = {}  # Definición global


@app.route("/chat", methods=["POST"])
def chat():
    pregunta_limpia = request.json.get("mensaje")
    pregunta_limpia = eliminar_acentos(pregunta_limpia.lower())

    # Obtener el valor de modo_administrador desde el frontend (si se envía)
    modo_administrador = request.json.get("modo_administrador", False)

    # Actualizar el valor en la sesión si cambia
    session['modo_administrador'] = modo_administrador

    # Registro de la acción
    registrar_accion(
        f"Modo administrador actualizado en sesión: {session['modo_administrador']}")

    global estado_confirmacion  # Indica que estás usando la variable global

    registrar_accion(f"Mensaje recibido: '{pregunta_limpia}'")
    registrar_accion(
        f"Estado de administrador desde sesión: {session.get('modo_administrador', False)}")

    # Modo administrador
    if session.get('modo_administrador', False):
        registrar_accion(
            f"Modo administrador activado para la pregunta: {pregunta_limpia}")

        # Llamada a entrenando_IA con modo_administrador=True
        respuesta_ia = entrenando_IA(
            pregunta_limpia, datos_previos, modo_administrador=True)
        if respuesta_ia:
            return jsonify({"respuesta": respuesta_ia})

        # Llamada a generar respuesta por similitud
        respuesta_ia = generar_respuesta_por_similitud(
            pregunta_limpia, datos_previos)
        if respuesta_ia:
            return jsonify({"respuesta": respuesta_ia})

        # Si el administrador busca en archivos
        respuesta_ia = buscar_en_archivos_uploads(pregunta_limpia)
        if respuesta_ia:
            return jsonify({"respuesta": respuesta_ia})

    # Si hay confirmación pendiente, manejarla primero
    if estado_confirmacion.get("confirmacion_pendiente"):
        if pregunta_limpia == "si":
            registrar_accion(
                "Usuario aceptó confirmar y seleccionará una categoría")
            return jsonify({
                "respuesta": "Por favor, selecciona una categoría para guardar: " + ', '.join(estado_confirmacion['categorias']),
                "categorias": estado_confirmacion['categorias']
            })
        elif pregunta_limpia == "no":
            registrar_accion("Usuario rechazó la confirmación pendiente")
            estado_confirmacion.clear()
            return jsonify({"respuesta": "La propuesta fue rechazada. Puedes hacer otra pregunta."})
        else:
            registrar_accion(
                "Usuario respondió con una entrada inválida durante la confirmación")
            return jsonify({"respuesta": "Por favor responde con 'si' o 'no'."})

    # Procesar normalmente si no hay confirmación pendiente
    # Primero, verificar si la pregunta es sobre "ver datos"
    if "ver datos" in pregunta_limpia:
        return ver_datos()

    # Verificar si la última pregunta fue sobre recetas y procesar la elección
    if conocimientos["contexto"]["ultimaPregunta"] in ["receta", "recetas", "postres"]:
        try:
            num_receta = int(pregunta_limpia.strip())
            respuesta_receta = comida(
                pregunta_limpia, conocimientos, num_receta)
            conocimientos["contexto"]["ultimaPregunta"] = None
            return jsonify({"respuesta": respuesta_receta})
        except ValueError:
            return jsonify({"respuesta": "Por favor, ingresa el número de la receta que deseas ver."})

    # Detectar palabras clave de recetas
    if "receta" in pregunta_limpia or "postres" in pregunta_limpia:
        conocimientos["contexto"]["ultimaPregunta"] = "receta"
        respuesta_receta = comida(pregunta_limpia, conocimientos)
        return jsonify({"respuesta": respuesta_receta})

    # Procesar con función de matemáticas
    respuesta_matematica = matematica(pregunta_limpia.lower())
    if respuesta_matematica and "No pude entender la operación" not in respuesta_matematica:
        return jsonify({"respuesta": respuesta_matematica})

    # Procesar el mensaje normalmente
    respuesta_ia = procesar_mensaje(pregunta_limpia, conocimientos, geografia_data,
                                    animales_data, datos_previos, session.get('modo_administrador', False))
    if respuesta_ia:
        return jsonify({"respuesta": respuesta_ia})

    # Respuesta genérica si no se encuentra nada
    return jsonify({"respuesta": "No entendí tu consulta, ¿puedes reformularla?"})


if __name__ == "__main__":
    app.run(debug=True)
