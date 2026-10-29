# ============================================================
# PROTEGE ANIMAL
# Aplicacion para reportar maltrato animal
#==============================================================

import os
import webbrowser
from datetime import datetime

import tkinter as tk
from tkinter import filedialog

# Modulos propios del proyecto
from busquedas import (
    busqueda_binaria,
    busqueda_lineal_matriz,
    correo_valido,
)
from persistencia import guardar_denuncias, cargar_denuncias

# ============================================================
# LIBRERIAS OPCIONALES
# ============================================================

try:
    import msvcrt
    MSVCRT_DISPONIBLE = True
except ImportError:
    MSVCRT_DISPONIBLE = False

try:
    import cv2
    CV2_DISPONIBLE = True
except ImportError:
    CV2_DISPONIBLE = False

try:
    import folium
    FOLIUM_DISPONIBLE = True
except ImportError:
    FOLIUM_DISPONIBLE = False

try:
    from plyer import notification
    PLYER_DISPONIBLE = True
except ImportError:
    PLYER_DISPONIBLE = False


# ============================================================
# VARIABLES GLOBALES
# ============================================================

# Lista de objetos Denuncia (se mantiene para mostrar los datos).
denuncias = []

# Matriz 2D: cada fila es una denuncia y cada columna un campo.
# Esta matriz es la que usan los algoritmos de busqueda.
matriz_denuncias = []

# Arreglo 1D con los numeros de denuncia. Como el contador
# siempre aumenta, queda ORDENADO, lo que permite busqueda binaria.
indice_numeros = []

contador_denuncia = 1
usuario_registrado = None

CARPETA_EVIDENCIAS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "evidencias"
)

RUTA_MAPA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "mapa_generado.html"
)


# ============================================================
# INDICES DE COLUMNAS DE LAS MATRICES
# ============================================================

# Columnas de las matrices REFUGIOS y VETERINARIAS
COL_NOMBRE = 0
COL_DIRECCION = 1
COL_TELEFONO = 2
COL_LAT = 3
COL_LON = 4

# Columnas de la matriz matriz_denuncias
D_NUMERO = 0
D_TIPO = 1
D_DESCRIPCION = 2
D_UBICACION = 3
D_FECHA = 4
D_FOTO = 5


# ============================================================
# DATOS DE REFUGIOS  (MATRIZ 2D)
# Columnas: nombre, direccion, telefono, latitud, longitud
# ============================================================

REFUGIOS = [
    ["Refugio Patitas Felices", "Colonia Centro",
     "22221111", 12.8654, -85.2072],
    ["Refugio Huellas de Amor", "Colonia San Jose",
     "22223333", 12.8700, -85.2100],
]


# ============================================================
# DATOS DE VETERINARIAS  (MATRIZ 2D)
# Columnas: nombre, direccion, telefono, latitud, longitud
# ============================================================

VETERINARIAS = [
    ["Veterinaria San Francisco", "Avenida Principal",
     "22226666", 12.8680, -85.2050],
    ["Clinica Vida Animal", "Zona Central",
     "22227777", 12.8720, -85.2020],
]


# ============================================================
# MOSTRAR Y ELEGIR SERVICIOS
# (los algoritmos de busqueda estan en busquedas.py)
# ============================================================


def mostrar_servicio(fila_servicio):

    print("\nNombre:", fila_servicio[COL_NOMBRE])
    print("Direccion:", fila_servicio[COL_DIRECCION])
    print("Telefono:", fila_servicio[COL_TELEFONO])


def elegir_servicio(matriz, posiciones):
    """
    A partir de un arreglo de posiciones encontradas, deja
    elegir una (si hay varias). Devuelve la fila o None.
    """

    if not posiciones:
        return None

    if len(posiciones) == 1:
        return matriz[posiciones[0]]

    print("\nSe encontraron varias coincidencias:")

    for numero in range(len(posiciones)):
        print(
            f"{numero + 1}. "
            f"{matriz[posiciones[numero]][COL_NOMBRE]}"
        )

    try:
        eleccion = int(input("Elija una opcion: "))
    except ValueError:
        print("Debe ingresar un numero.")
        return None

    if 1 <= eleccion <= len(posiciones):
        return matriz[posiciones[eleccion - 1]]

    print("Opcion fuera de rango.")
    return None



# ============================================================
# OCULTAR CONTRASENA
# ============================================================

def ocultar_contrasena(mensaje):

    if not MSVCRT_DISPONIBLE:
        import getpass
        return getpass.getpass(mensaje)

    print(mensaje, end="", flush=True)
    contrasena = ""

    while True:

        tecla = msvcrt.getch()

        if tecla == b"\r":
            print()
            break

        elif tecla == b"\x08":

            if contrasena:
                contrasena = contrasena[:-1]
                print("\b \b", end="", flush=True)

        elif tecla in (b"\x00", b"\xe0"):
            msvcrt.getch()

        else:

            try:
                caracter = tecla.decode("utf-8")

                if caracter.isprintable():
                    contrasena += caracter
                    print("*", end="", flush=True)

            except UnicodeDecodeError:
                pass

    return contrasena


# ============================================================
# 1. CREAR CUENTA
# ============================================================

def crear_una_cuenta():

    print("\n===== CREAR CUENTA =====")

    try:

        nombre = input("Ingrese su nombre: ").strip()

        if not nombre:
            print("El nombre es obligatorio.")
            return None

        if not nombre.replace(" ", "").isalpha():
            print("El nombre solo debe contener letras.")
            return None

        # Solicitar el correo despues de validar el nombre.
        correo = input(
            "Ingrese su correo electronico: "
        ).strip()

        # Esta validacion permite numeros en el correo.
        if not correo_valido(correo):
            print("Correo no valido.")
            print("Ejemplo: usuario123@gmail.com")
            return None

        contrasena = ocultar_contrasena(
            "Ingrese su contrasena: "
        )

        if not contrasena:
            print("La contrasena no puede estar vacia.")
            return None

        confirmar = ocultar_contrasena(
            "Confirme su contrasena: "
        )

        if contrasena != confirmar:
            print("Las contrasenas no coinciden.")
            return None

        usuario = {
            "nombre": nombre,
            "correo": correo,
            "contrasena": contrasena
        }

        print("\nCuenta creada correctamente.")

        return usuario

    except (ValueError, EOFError, KeyboardInterrupt) as error:
        print("No se pudo crear la cuenta:", error)
        return None


# ============================================================
# 2. INICIAR SESION
# ============================================================

def iniciar_sesion(usuario):

    print("\n===== INICIAR SESION =====")

    if usuario is None:
        print("Primero debe crear una cuenta.")
        return False

    try:

        correo = input("Ingrese su correo: ").strip()

        if not correo_valido(correo):
            print("El correo no es valido.")
            return False

        contrasena = ocultar_contrasena(
            "Ingrese su contrasena: "
        )

        if (
            correo.lower() == usuario["correo"].lower()
            and contrasena == usuario["contrasena"]
        ):

            print("\nBienvenido", usuario["nombre"])
            print("Inicio de sesion exitoso.")

            return True

        print("Correo o contrasena incorrectos.")
        return False

    except (ValueError, EOFError, KeyboardInterrupt) as error:
        print("Error al iniciar sesion:", error)
        return False


# ============================================================
# CLASE DENUNCIA
# ============================================================

class Denuncia:

    def __init__(
        self,
        numero,
        tipo_maltrato,
        descripcion,
        ubicacion,
        fecha
    ):

        self.numero = numero
        self.tipo_maltrato = tipo_maltrato
        self.descripcion = descripcion
        self.ubicacion = ubicacion
        self.fecha = fecha
        self.fotografia = None

    def mostrar_denuncia(self):

        print("\n------------------------------")
        print("Numero:", self.numero)
        print("Tipo de maltrato:", self.tipo_maltrato)
        print("Descripcion:", self.descripcion)
        print("Ubicacion:", self.ubicacion)
        print("Fecha:", self.fecha)

        if self.fotografia:
            print("Fotografia:", self.fotografia)
        else:
            print("Fotografia: Sin fotografia")

        print("------------------------------")


# ============================================================
# 3. REGISTRAR DENUNCIA
# ============================================================

def registrar_denuncia():

    global contador_denuncia

    print("\n===== REGISTRAR DENUNCIA =====")

    try:

        tipo = input(
            "Tipo de maltrato animal: "
        ).strip()

        if not tipo or not any(c.isalpha() for c in tipo):
            print("Ingrese un tipo de maltrato valido.")
            return None

        descripcion = input(
            "Descripcion del caso: "
        ).strip()

        if not descripcion:
            print("La descripcion es obligatoria.")
            return None

        ubicacion = input(
            "Ubicacion del animal: "
        ).strip()

        if not ubicacion:
            print("La ubicacion es obligatoria.")
            return None

        fecha = input(
            "Fecha (DD/MM/AAAA): "
        ).strip()

        fecha_correcta = datetime.strptime(
            fecha,
            "%d/%m/%Y"
        )

        denuncia = Denuncia(
            contador_denuncia,
            tipo,
            descripcion,
            ubicacion,
            fecha_correcta.strftime("%d/%m/%Y")
        )

        # Se guardan los tres arreglos en la MISMA posicion:
        #   denuncias[i], matriz_denuncias[i], indice_numeros[i]
        denuncias.append(denuncia)

        matriz_denuncias.append([
            denuncia.numero,
            denuncia.tipo_maltrato,
            denuncia.descripcion,
            denuncia.ubicacion,
            denuncia.fecha,
            None
        ])

        indice_numeros.append(denuncia.numero)

        contador_denuncia += 1

        # Persistencia: se guarda la matriz en el archivo JSON.
        guardar_denuncias(matriz_denuncias, contador_denuncia)

        print("\nDenuncia registrada correctamente.")
        print("Numero de denuncia:", denuncia.numero)

        return denuncia

    except ValueError:
        print("Error: revise los datos y la fecha.")
        print("Use el formato DD/MM/AAAA.")
        return None

    except (EOFError, KeyboardInterrupt):
        print("\nRegistro cancelado.")
        return None


# ============================================================
# 4. VER DENUNCIAS
# ============================================================

def ver_denuncias():

    print("\n===== DENUNCIAS REGISTRADAS =====")

    if len(denuncias) == 0:
        print("No hay denuncias registradas.")
        return

    for denuncia in denuncias:
        denuncia.mostrar_denuncia()


# ============================================================
# 5. BUSCAR DENUNCIA  (MATRIZ + BUSQUEDA BINARIA / LINEAL)
# ============================================================

def buscar_denuncia():

    print("\n===== BUSCAR DENUNCIA =====")

    if not matriz_denuncias:
        print("No hay denuncias registradas.")
        return

    print("1. Por numero de denuncia")
    print("2. Por tipo de maltrato")
    print("3. Por ubicacion")
    print("4. Por palabra clave (tipo, descripcion o ubicacion)")

    opcion = input("Seleccione una opcion: ").strip()

    # ---- Busqueda binaria sobre el arreglo 1D ordenado ----
    if opcion == "1":

        try:
            numero = int(
                input("Ingrese el numero de denuncia: ")
            )
        except ValueError:
            print("Debe ingresar un numero entero.")
            return

        posicion = busqueda_binaria(indice_numeros, numero)

        if posicion == -1:
            print("No se encontro esa denuncia.")
            return

        print("Denuncia encontrada.")
        denuncias[posicion].mostrar_denuncia()
        return

    # ---- Busqueda lineal sobre columnas de la matriz ----
    if opcion == "2":
        columnas = [D_TIPO]
        texto = input("Tipo de maltrato a buscar: ")

    elif opcion == "3":
        columnas = [D_UBICACION]
        texto = input("Ubicacion a buscar: ")

    elif opcion == "4":
        columnas = [D_TIPO, D_DESCRIPCION, D_UBICACION]
        texto = input("Palabra clave: ")

    else:
        print("Opcion no valida.")
        return

    if not texto.strip():
        print("Debe escribir algo para buscar.")
        return

    posiciones = busqueda_lineal_matriz(
        matriz_denuncias,
        columnas,
        texto
    )

    if not posiciones:
        print("No se encontraron denuncias con ese dato.")
        return

    print(f"\nSe encontraron {len(posiciones)} denuncia(s).")

    for posicion in posiciones:
        denuncias[posicion].mostrar_denuncia()


# ============================================================
# 6. DESCRIPCION DEL REPORTE
# ============================================================

def descripcion_reporte():

    print("\n===== DESCRIPCION DEL REPORTE =====")

    try:

        ocurrido = input(
            "Que ocurrio?: "
        ).strip()

        animal = input(
            "Que animal fue afectado?: "
        ).strip()

        informacion = input(
            "Informacion adicional: "
        ).strip()

        if not ocurrido or not animal or not informacion:
            print("Todos los campos son obligatorios.")
            return

        print("\nDescripcion del reporte:")
        print("Lo ocurrido:", ocurrido)
        print("Animal afectado:", animal)
        print("Informacion adicional:", informacion)

    except (ValueError, EOFError, KeyboardInterrupt) as error:
        print("Error:", error)


# ============================================================
# SELECCIONAR FOTOGRAFIA DE LA GALERIA
# ============================================================

def seleccionar_fotografia():

    ventana = None

    try:

        ventana = tk.Tk()
        ventana.withdraw()

        ruta = filedialog.askopenfilename(
            title="Seleccionar fotografia",
            filetypes=[
                ("Imagenes", "*.jpg *.jpeg *.png *.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )

        return ruta if ruta else None

    except Exception as error:
        print("Error al abrir la galeria:", error)
        return None

    finally:

        if ventana is not None:
            ventana.destroy()


# ============================================================
# TOMAR FOTOGRAFIA CON LA CAMARA
# ============================================================

def tomar_fotografia():

    if not CV2_DISPONIBLE:
        print("La camara requiere opencv-python.")
        print("Instale con: pip install opencv-python")
        return None

    camara = None

    try:

        os.makedirs(
            CARPETA_EVIDENCIAS,
            exist_ok=True
        )

        camara = cv2.VideoCapture(0)

        if not camara.isOpened():
            print("No se pudo abrir la camara.")
            return None

        fotografia = None

        print("Presione ESPACIO para capturar.")
        print("Presione ESC para cancelar.")

        while True:

            correcto, imagen = camara.read()

            if not correcto:
                print("No se pudo obtener la imagen.")
                break

            cv2.imshow("PROTEGE ANIMAL", imagen)

            tecla = cv2.waitKey(1) & 0xFF

            if tecla == 27:
                break

            if tecla == 32:

                nombre = datetime.now().strftime(
                    "evidencia_%Y%m%d_%H%M%S.png"
                )

                fotografia = os.path.join(
                    CARPETA_EVIDENCIAS,
                    nombre
                )

                if cv2.imwrite(fotografia, imagen):
                    print("Fotografia guardada:", fotografia)
                else:
                    print("No se pudo guardar la fotografia.")
                    fotografia = None

                break

        return fotografia

    except Exception as error:
        print("Error con la camara:", error)
        return None

    finally:

        if camara is not None:
            camara.release()

        if CV2_DISPONIBLE:
            cv2.destroyAllWindows()


# ============================================================
# 7. SUBIR FOTOGRAFIA A UNA DENUNCIA  (BUSQUEDA BINARIA)
# ============================================================

def subir_fotografias():

    print("\n===== SUBIR FOTOGRAFIA =====")

    if not denuncias:
        print("Primero debe registrar una denuncia.")
        return

    try:

        numero = int(
            input("Numero de la denuncia: ")
        )

    except ValueError:
        print("Ingrese un numero valido.")
        return

    # Busqueda binaria en el arreglo 1D de numeros.
    posicion = busqueda_binaria(indice_numeros, numero)

    if posicion == -1:
        print("No se encontro esa denuncia.")
        return

    print("\n1. Seleccionar desde galeria")
    print("2. Tomar fotografia con camara")

    opcion = input("Seleccione una opcion: ").strip()

    if opcion == "1":
        fotografia = seleccionar_fotografia()

    elif opcion == "2":
        fotografia = tomar_fotografia()

    else:
        print("Opcion no valida.")
        return

    if fotografia:

        # Se actualiza el objeto y tambien la matriz.
        denuncias[posicion].fotografia = fotografia
        matriz_denuncias[posicion][D_FOTO] = fotografia

        guardar_denuncias(matriz_denuncias, contador_denuncia)

        print("Fotografia asociada correctamente.")
        print("Archivo:", fotografia)

    else:
        print("No se selecciono ninguna fotografia.")


# ============================================================
# MOSTRAR REFUGIOS  (RECORRIDO DE MATRIZ)
# ============================================================

def mostrar_refugios():

    print("\n===== REFUGIOS =====")

    for fila in range(len(REFUGIOS)):
        mostrar_servicio(REFUGIOS[fila])


# ============================================================
# MOSTRAR VETERINARIAS  (RECORRIDO DE MATRIZ)
# ============================================================

def mostrar_veterinarias():

    print("\n===== VETERINARIAS =====")

    for fila in range(len(VETERINARIAS)):
        mostrar_servicio(VETERINARIAS[fila])


# ============================================================
# BUSCAR REFUGIOS / VETERINARIAS  (BUSQUEDA EN MATRIZ)
# ============================================================

def buscar_en_servicios(matriz, titulo):

    print(f"\n===== BUSCAR {titulo} =====")
    print("1. Por nombre o direccion")

    opcion = input("Seleccione una opcion: ").strip()

    if opcion == "1":

        texto = input("Escriba el nombre o la direccion: ")

        posiciones = busqueda_lineal_matriz(
            matriz,
            [COL_NOMBRE, COL_DIRECCION],
            texto
        )

        if not posiciones:
            print("No se encontraron resultados.")
            return

        print(f"\nSe encontraron {len(posiciones)} resultado(s).")

        for posicion in posiciones:
            mostrar_servicio(matriz[posicion])

    else:
        print("Opcion no valida.")


def buscar_refugio():
    buscar_en_servicios(REFUGIOS, "REFUGIO")


def buscar_veterinaria():
    buscar_en_servicios(VETERINARIAS, "VETERINARIA")


# ============================================================
# MOSTRAR MAPA
# ============================================================

def mostrar_mapa():

    if not FOLIUM_DISPONIBLE:
        print("Instale folium con: pip install folium")
        return

    try:

        mapa = folium.Map(
            location=[12.8654, -85.2072],
            zoom_start=13
        )

        for fila in range(len(REFUGIOS)):

            folium.Marker(
                [REFUGIOS[fila][COL_LAT], REFUGIOS[fila][COL_LON]],
                popup=REFUGIOS[fila][COL_NOMBRE]
            ).add_to(mapa)

        for fila in range(len(VETERINARIAS)):

            folium.Marker(
                [
                    VETERINARIAS[fila][COL_LAT],
                    VETERINARIAS[fila][COL_LON]
                ],
                popup=VETERINARIAS[fila][COL_NOMBRE]
            ).add_to(mapa)

        mapa.save(RUTA_MAPA)

        webbrowser.open(
            "file://" + os.path.abspath(RUTA_MAPA)
        )

        print("Mapa abierto correctamente.")

    except Exception as error:
        print("Error al generar el mapa:", error)


# ============================================================
# ENVIAR NOTIFICACION
# ============================================================

def enviar_notificacion():

    mensaje = input(
        "Escriba el mensaje de alerta: "
    ).strip()

    if not mensaje:
        print("El mensaje no puede estar vacio.")
        return

    if PLYER_DISPONIBLE:

        try:

            notification.notify(
                title="PROTEGE ANIMAL",
                message=mensaje,
                timeout=5
            )

            print("Notificacion enviada.")

        except Exception as error:
            print("No se pudo enviar la notificacion:", error)

    else:

        print("\n===== ALERTA =====")
        print(mensaje)
        print("Para notificaciones del sistema instale plyer.")


# ============================================================
# LLAMAR A UN SERVICIO  (BUSQUEDA EN MATRIZ)
# ============================================================

def llamar_directamente():

    print("\n===== LLAMAR DIRECTAMENTE =====")
    print("1. Refugio")
    print("2. Veterinaria")
    print("3. Introducir otro numero")

    opcion = input("Seleccione una opcion: ").strip()

    if opcion == "1" or opcion == "2":

        if opcion == "1":
            matriz = REFUGIOS
            mostrar_refugios()
            texto = input("Escriba el nombre del refugio: ")
        else:
            matriz = VETERINARIAS
            mostrar_veterinarias()
            texto = input("Escriba el nombre de la veterinaria: ")

        # Busqueda parcial por nombre: no hace falta escribirlo completo.
        posiciones = busqueda_lineal_matriz(
            matriz,
            [COL_NOMBRE],
            texto
        )

        servicio = elegir_servicio(matriz, posiciones)

        if servicio is None:
            if not posiciones:
                print("No se encontro el servicio.")
            return

        webbrowser.open("tel:" + servicio[COL_TELEFONO])
        print("Solicitud de llamada abierta a", servicio[COL_NOMBRE])

    elif opcion == "3":

        telefono = input(
            "Ingrese el numero telefonico: "
        ).strip()

        if telefono:
            webbrowser.open("tel:" + telefono)
            print("Solicitud de llamada abierta.")
        else:
            print("Debe ingresar un numero.")

    else:
        print("Opcion no valida.")


# ============================================================
# SERVICIOS ADICIONALES
# ============================================================

def servicios_adicionales():

    while True:

        print("\n===== SERVICIOS DE AYUDA =====")
        print("1. Ver refugios")
        print("2. Ver veterinarias")
        print("3. Buscar refugio")
        print("4. Buscar veterinaria")
        print("5. Mostrar mapa")
        print("6. Enviar notificacion")
        print("7. Llamar directamente")
        print("8. Volver")

        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "1":
            mostrar_refugios()

        elif opcion == "2":
            mostrar_veterinarias()

        elif opcion == "3":
            buscar_refugio()

        elif opcion == "4":
            buscar_veterinaria()

        elif opcion == "5":
            mostrar_mapa()

        elif opcion == "6":
            enviar_notificacion()

        elif opcion == "7":
            llamar_directamente()

        elif opcion == "8":
            break

        else:
            print("Opcion no valida.")


# ============================================================
# MENU PRINCIPAL
# ============================================================

def menu():

    usuario = None
    sesion_iniciada = False

    while True:

        print("\n================================")
        print("        PROTEGE ANIMAL")
        print("================================")
        print("1. Crear cuenta")
        print("2. Iniciar sesion")
        print("3. Registrar denuncia")
        print("4. Ver denuncias")
        print("5. Buscar denuncia")
        print("6. Descripcion del reporte")
        print("7. Subir fotografia")
        print("8. Servicios y salir")

        opcion = input(
            "Seleccione una opcion: "
        ).strip()

        if opcion == "1":

            nuevo_usuario = crear_una_cuenta()

            if nuevo_usuario is not None:
                usuario = nuevo_usuario
                sesion_iniciada = False

        elif opcion == "2":

            if usuario is None:
                print("Primero debe crear una cuenta.")

            else:
                sesion_iniciada = iniciar_sesion(usuario)

        elif opcion == "3":

            if not sesion_iniciada:
                print("Primero debe iniciar sesion.")

            else:
                registrar_denuncia()

        # OPCION 4: NO REQUIERE INICIAR SESION
        elif opcion == "4":
            ver_denuncias()

        elif opcion == "5":

            if not sesion_iniciada:
                print("Primero debe iniciar sesion.")

            else:
                buscar_denuncia()

        elif opcion == "6":

            if not sesion_iniciada:
                print("Primero debe iniciar sesion.")

            else:
                descripcion_reporte()

        elif opcion == "7":

            if not sesion_iniciada:
                print("Primero debe iniciar sesion.")

            else:
                subir_fotografias()

        elif opcion == "8":

            print("\n1. Servicios de ayuda")
            print("2. Cerrar sesion")
            print("3. Salir del programa")

            subopcion = input(
                "Seleccione una opcion: "
            ).strip()

            if subopcion == "1":
                servicios_adicionales()

            elif subopcion == "2":

                if sesion_iniciada:
                    sesion_iniciada = False
                    print("Sesion cerrada correctamente.")
                else:
                    print("No hay una sesion iniciada.")

            elif subopcion == "3":
                print("Gracias por utilizar PROTEGE ANIMAL.")
                break

            else:
                print("Opcion no valida.")

        else:
            print("Opcion no valida. Elija del 1 al 8.")


# ============================================================
# EJECUTAR PROGRAMA
# ============================================================

def cargar_datos():
    """
    Lee el archivo JSON al iniciar y reconstruye los tres
    arreglos: matriz_denuncias, indice_numeros y denuncias.
    """

    global contador_denuncia

    matriz, contador = cargar_denuncias()

    for fila in matriz:

        denuncia = Denuncia(
            fila[D_NUMERO],
            fila[D_TIPO],
            fila[D_DESCRIPCION],
            fila[D_UBICACION],
            fila[D_FECHA]
        )
        denuncia.fotografia = fila[D_FOTO]

        denuncias.append(denuncia)
        matriz_denuncias.append(fila)
        indice_numeros.append(denuncia.numero)

    contador_denuncia = contador

    if matriz:
        print(f"Se cargaron {len(matriz)} denuncia(s) guardadas.")


if __name__ == "__main__":
    try:
        cargar_datos()
        menu()
    except KeyboardInterrupt:
        print("\nPrograma finalizado.")