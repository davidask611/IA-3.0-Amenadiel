from Amenadiel import re, math
# Funcion matematica


def matematica(pregunta):
    # Reemplazar 'pi' por su valor aproximado (3.14)
    pregunta = pregunta.replace("pi", "3.14")

    # Reemplazar ^ por ** para potencias
    pregunta = pregunta.replace("^", "**")

    # Buscar y calcular todas las raíces cuadradas en la expresión
    def calcular_raiz_cuadrada(expresion):
        matches = re.findall(r'raiz cuadrada de (\d+)', expresion.lower())
        for match in matches:
            numero = int(match)
            raiz_cuadrada = round(math.sqrt(numero), 3)
            expresion = expresion.replace(
                f"raiz cuadrada de {match}", str(raiz_cuadrada))
        return expresion

    # Buscar y calcular todas las raíces cúbicas en la expresión
    def calcular_raiz_cubica(expresion):
        matches = re.findall(r'raiz cubica de (\d+)', expresion.lower())
        for match in matches:
            numero = int(match)
            raiz_cubica = round(math.pow(numero, 1/3), 3)
            expresion = expresion.replace(
                f"raiz cubica de {match}", str(raiz_cubica))
        return expresion

    # Buscar y calcular porcentajes en la expresión
    def calcular_porcentaje(expresion):
        # Buscar expresiones del tipo "20% de 50"
        matches = re.findall(r'(\d+)% de (\d+)', expresion.lower())
        for porcentaje, numero in matches:
            resultado = (int(porcentaje) / 100) * int(numero)
            expresion = expresion.replace(
                f"{porcentaje}% de {numero}", str(resultado))
        return expresion

    # Reemplazar log() por math.log(), esperando formato log(base, numero)
    def calcular_logaritmo(expresion):
        matches = re.findall(r'log\((\d+),\s*(\d+)\)', expresion)
        for base, numero in matches:
            logaritmo = round(math.log(int(numero), int(base)), 3)
            expresion = expresion.replace(
                f"log({base}, {numero})", str(logaritmo))
        return expresion

    # Buscar y reemplazar funciones trigonométricas por sus equivalentes en radianes
    def calcular_trigonometria(expresion):
        trig_functions = {"sin": math.sin, "cos": math.cos, "tan": math.tan}
        for func in trig_functions:
            matches = re.findall(rf'{func}\((\d+)\)', expresion)
            for match in matches:
                angulo_en_grados = int(match)
                angulo_en_radianes = math.radians(
                    angulo_en_grados)  # Convertir a radianes
                resultado_trig = round(
                    trig_functions[func](angulo_en_radianes), 3)
                expresion = expresion.replace(
                    f"{func}({match})", str(resultado_trig))
        return expresion

    # Aplicar todas las funciones anteriores a la pregunta
    pregunta_limpia = calcular_raiz_cuadrada(pregunta.lower())
    pregunta_limpia = calcular_raiz_cubica(pregunta_limpia)
    pregunta_limpia = calcular_porcentaje(
        pregunta_limpia)  # Aquí calculamos porcentajes
    pregunta_limpia = calcular_logaritmo(pregunta_limpia)
    pregunta_limpia = calcular_trigonometria(pregunta_limpia)

    # Validar operaciones usando eval
    try:
        # Validar que solo contenga caracteres permitidos antes de usar eval
        if re.match(r'^[\d\.\+\-\*/\(\)%\^ ]+$', pregunta_limpia):
            resultado = eval(pregunta_limpia)

            # Formatear el resultado: sin decimales si es un número entero, o con tres decimales si tiene decimales.
            if isinstance(resultado, float) and resultado.is_integer():
                resultado = int(resultado)
            else:
                resultado = round(resultado, 3)

            return f"El resultado de {pregunta} es {resultado}."
        else:
            return "No pude entender la operación, intenta de nuevo con una operación simple."
    except (SyntaxError, ZeroDivisionError) as e:
        return f"Error en la operación: {e}. Por favor, revisa la sintaxis."
