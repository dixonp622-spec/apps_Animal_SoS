# ============================================================
# MODULO DE PERSISTENCIA (JSON) - PROTEGE ANIMAL
# ============================================================

import json
import os

RUTA_DATOS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "denuncias.json"
)


def guardar_denuncias(matriz, contador, ruta=RUTA_DATOS):
    """
    Escribe la matriz de denuncias y el siguiente numero de
    denuncia en un archivo JSON. Devuelve True si se guardo.
    """

    datos = {
        "contador": contador,
        "denuncias": matriz
    }

    try:

        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)

        return True

    except OSError as error:
        print("No se pudo guardar el archivo:", error)
        return False


def cargar_denuncias(ruta=RUTA_DATOS):
    """
    Lee el archivo JSON. Devuelve (matriz, contador).
    Si el archivo no existe o esta danado, devuelve ([], 1)
    para que el programa pueda iniciar sin datos.
    """

    if not os.path.exists(ruta):
        return [], 1

    try:

        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        matriz = datos["denuncias"]
        contador = int(datos["contador"])

        return matriz, contador

    except (OSError, ValueError, KeyError, TypeError):
        print("El archivo de datos esta danado. Se inicia vacio.")
        return [], 1
