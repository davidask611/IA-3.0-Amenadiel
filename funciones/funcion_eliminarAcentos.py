import unicodedata
def eliminar_acentos(texto):
    """
    Elimina los acentos y tildes de un texto dado.
    También reemplaza la ñ por un símbolo temporal para mantener su presencia.
    """
    texto = texto.replace("ñ", "~").replace("Ñ", "~")
    texto_normalizado = unicodedata.normalize("NFD", texto)
    texto_sin_acentos = "".join(
        c for c in texto_normalizado if unicodedata.category(c) != "Mn"
    )
    texto_final = texto_sin_acentos.replace("~", "ñ")
    return texto_final