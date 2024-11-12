import json
from flask import Flask, render_template, request, jsonify, session
from Amenadiel import procesar_mensaje, ver_datos as obtener_datos, conocimientos, geografia
import os

app = Flask(__name__)

# Configuración de clave secreta para la sesión
app.secret_key = 'clave_secreta'  # Asegúrate de que sea única y segura


@app.route("/", methods=["GET"])
def home():
    session['modo_administrador'] = False  # Restablecer a False en cada carga
    return render_template("index.html")


# Endpoint para ver datos


@app.route("/ver_datos", methods=["POST"])
def ver_datos():
    # Verificación de acceso para modo administrador
    if not session.get('modo_administrador', False):
        print("Intento de acceso sin privilegios de administrador")
        return jsonify({"respuesta": "No tienes acceso para ver los datos."})

    # Obtener lista de archivos JSON en el directorio
    directorio_json = '.'  # Cambiar a la ruta que desees
    archivos_json = [f for f in os.listdir(
        directorio_json) if f.endswith('.json')]

    if archivos_json:
        respuesta = "Archivos JSON disponibles:\n" + "\n".join(archivos_json)
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


# Ruta para manejar el chat y activar modo administrador si se requiere
@app.route("/chat", methods=["POST"])
def chat():
    mensaje = request.json.get("mensaje")
    es_administrador = request.json.get("es_administrador", False)

    # Activar modo administrador en la sesión si corresponde
    if es_administrador:
        session['modo_administrador'] = True
        print("Modo administrador activado en sesión.")

    print(f"Mensaje recibido en Flask: '{mensaje}'")
    print(f"Estado de administrador: {
          session.get('modo_administrador', False)}")

    # Procesar el mensaje recibido
    respuesta = procesar_mensaje(
        mensaje, conocimientos, geografia, es_administrador=session['modo_administrador'])
    print(f"Respuesta generada: {respuesta}")

    return jsonify({"respuesta": respuesta})


if __name__ == "__main__":
    app.run(debug=True)
