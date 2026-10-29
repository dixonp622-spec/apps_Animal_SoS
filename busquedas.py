# ============================================================
# MODULO DE BUSQUEDAS Y VALIDACIONES - PROTEGE ANIMAL
# ============================================================

import unicodedata


def normalizar(texto):
    """Pasa a minusculas y quita acentos para comparar mejor."""

    texto = str(texto).strip().lower()
    descompuesto = unicodedata.normalize("NFD", texto)

    return "".join(
        c for c in descompuesto
        if unicodedata.category(c) != "Mn"
    )


def busqueda_binaria(arreglo, objetivo):

    izquierda = 0
    derecha = len(arreglo) - 1

    while izquierda <= derecha:

        medio = (izquierda + derecha) // 2

        if arreglo[medio] == objetivo:
            return medio

        if arreglo[medio] < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio - 1

    return -1


def busqueda_lineal_matriz(matriz, columnas, texto):

    buscado = normalizar(texto)
    encontradas = []

    if not buscado:
        return encontradas

    for fila in range(len(matriz)):

        for columna in columnas:

            if buscado in normalizar(matriz[fila][columna]):
                encontradas.append(fila)
                break

    return encontradas


def correo_valido(correo):
    

    correo = correo.strip()

    if not correo or any(c.isspace() for c in correo):
        return False

    if correo.count("@") != 1:
        return False

    nombre, dominio = correo.split("@")

    if not nombre or not dominio:
        return False

    caracteres_validos = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789._+-"
    )

    if not all(c in caracteres_validos for c in nombre):
        return False

    if "." not in dominio:
        return False

    if dominio.startswith(".") or dominio.endswith("."):
        return False

    if ".." in correo:
        return False

    partes_dominio = dominio.split(".")

    if any(not parte for parte in partes_dominio):
        return False

    if any(
        not all(c.isalnum() or c == "-" for c in parte)
        for parte in partes_dominio
    ):
        return False

    # La terminacion debe tener al menos dos letras.
    if (
        len(partes_dominio[-1]) < 2
        or not partes_dominio[-1].isalpha()
    ):
        return False

    return True
