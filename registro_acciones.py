import os
import datetime


def registrar_accion(accion):
    """
    Registra una acción en el archivo registro.log.
    Si el archivo no existe, se crea automáticamente.
    """
    try:
        # Verificar si el archivo existe (opcional, no es estrictamente necesario con "a")
        if not os.path.exists("registro.log"):
            with open("registro.log", "w") as archivo:
                archivo.write("Registro de acciones iniciado.\n")

        # Obtener la fecha y hora actual
        ahora = datetime.datetime.now()
        fecha_hora = ahora.strftime("%Y-%m-%d %H:%M:%S")

        # Registrar la acción en el archivo
        with open("registro.log", "a", encoding="utf-8") as archivo:
            archivo.write(f"{fecha_hora} - {accion}\n")
    except Exception as e:
        print(f"Error al registrar la acción: {str(e)}")
