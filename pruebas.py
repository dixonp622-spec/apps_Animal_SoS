# ============================================================
# PRUEBAS UNITARIAS CON ASSERT - PROTEGE ANIMAL
# ============================================================

import os
import tempfile

from busquedas import (
    normalizar,
    busqueda_binaria,
    busqueda_lineal_matriz,
    correo_valido,
)
from persistencia import guardar_denuncias, cargar_denuncias


# Columnas de la matriz de denuncias:
# numero, tipo, descripcion, ubicacion, fecha, foto
MATRIZ_PRUEBA = [
    [1, "Abandono", "Perro sin comida", "Colonia Centro", "01/10/2026", None],
    [2, "Golpes", "Gato herido", "Colonia San Jose", "02/10/2026", None],
    [3, "Abandono", "Cachorros en la calle", "Zona Central", "03/10/2026", None],
]


# ---------------- normalizar ----------------

def prueba_normalizar():
    assert normalizar("  ÁBANDONO ") == "abandono"
    assert normalizar("Colonia José") == "colonia jose"
    assert normalizar("") == ""


# ---------------- busqueda binaria ----------------

def prueba_binaria_encuentra():
    arreglo = [1, 2, 3, 4, 5]
    assert busqueda_binaria(arreglo, 1) == 0     # primer elemento
    assert busqueda_binaria(arreglo, 3) == 2     # elemento del medio
    assert busqueda_binaria(arreglo, 5) == 4     # ultimo elemento


def prueba_binaria_no_encuentra():
    arreglo = [1, 2, 3, 4, 5]
    assert busqueda_binaria(arreglo, 99) == -1
    assert busqueda_binaria(arreglo, 0) == -1


def prueba_binaria_arreglo_vacio():
    assert busqueda_binaria([], 1) == -1


# ---------------- busqueda lineal sobre matriz ----------------

def prueba_lineal_por_tipo():
    # columna 1 = tipo de maltrato
    assert busqueda_lineal_matriz(MATRIZ_PRUEBA, [1], "abandono") == [0, 2]


def prueba_lineal_ignora_acentos_y_mayusculas():
    assert busqueda_lineal_matriz(MATRIZ_PRUEBA, [3], "SAN JOSÉ") == [1]


def prueba_lineal_coincidencia_parcial():
    # columna 2 = descripcion
    assert busqueda_lineal_matriz(MATRIZ_PRUEBA, [2], "gato") == [1]


def prueba_lineal_varias_columnas():
    # busca en tipo, descripcion y ubicacion a la vez
    assert busqueda_lineal_matriz(MATRIZ_PRUEBA, [1, 2, 3], "central") == [2]


def prueba_lineal_sin_resultados():
    assert busqueda_lineal_matriz(MATRIZ_PRUEBA, [1], "veneno") == []


def prueba_lineal_texto_vacio():
    assert busqueda_lineal_matriz(MATRIZ_PRUEBA, [1], "   ") == []


# ---------------- validacion de correo ----------------

def prueba_correo_valido():
    assert correo_valido("usuario123@gmail.com") is True
    assert correo_valido("ana.perez@correo.edu.ni") is True


def prueba_correo_invalido():
    assert correo_valido("") is False
    assert correo_valido("sin_arroba.com") is False
    assert correo_valido("dos@@gmail.com") is False
    assert correo_valido("usuario@gmail") is False
    assert correo_valido("con espacio@gmail.com") is False
    assert correo_valido("usuario@gmail.c") is False


# ---------------- persistencia JSON ----------------

def prueba_guardar_y_cargar():
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = os.path.join(carpeta, "datos.json")

        assert guardar_denuncias(MATRIZ_PRUEBA, 4, ruta) is True

        matriz, contador = cargar_denuncias(ruta)

        assert matriz == MATRIZ_PRUEBA
        assert contador == 4


def prueba_cargar_archivo_inexistente():
    matriz, contador = cargar_denuncias("no_existe_este_archivo.json")
    assert matriz == []
    assert contador == 1


def prueba_cargar_archivo_danado():
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = os.path.join(carpeta, "danado.json")

        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write("esto no es json {{{")

        matriz, contador = cargar_denuncias(ruta)

        assert matriz == []
        assert contador == 1


# ---------------- ejecutar todo ----------------

PRUEBAS = [
    prueba_normalizar,
    prueba_binaria_encuentra,
    prueba_binaria_no_encuentra,
    prueba_binaria_arreglo_vacio,
    prueba_lineal_por_tipo,
    prueba_lineal_ignora_acentos_y_mayusculas,
    prueba_lineal_coincidencia_parcial,
    prueba_lineal_varias_columnas,
    prueba_lineal_sin_resultados,
    prueba_lineal_texto_vacio,
    prueba_correo_valido,
    prueba_correo_invalido,
    prueba_guardar_y_cargar,
    prueba_cargar_archivo_inexistente,
    prueba_cargar_archivo_danado,
]


if __name__ == "__main__":

    for prueba in PRUEBAS:
        prueba()
        print("OK  ", prueba.__name__)

    print(f"\nTODAS LAS PRUEBAS PASARON ({len(PRUEBAS)})")
