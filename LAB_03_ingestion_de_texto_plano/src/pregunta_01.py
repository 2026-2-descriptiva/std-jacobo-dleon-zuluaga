import re

import pandas as pd


def pregunta_01():
    """
    El archivo `data/clusters_report.txt` es un reporte de clústeres de
    palabras clave pensado para ser leído por una persona, no por un programa:
    los encabezados ocupan varias líneas, las columnas están alineadas con
    espacios y la lista de palabras clave de un clúster continúa en las líneas
    siguientes.

    Su tarea es convertir ese reporte en un DataFrame de Pandas con una fila
    por clúster y las columnas:

    - `cluster`: número del clúster, como entero.
    - `cantidad_de_palabras_clave`: como entero.
    - `porcentaje_de_palabras_clave`: como número decimal; por ejemplo, el
      texto `15,9 %` debe quedar como `15.9`.
    - `principales_palabras_clave`: todas las palabras clave del clúster en un
      solo texto, separadas por una coma y un único espacio.

    Retorne el DataFrame.

    Ejemplo del formato de la respuesta (se omite la última columna):

           cluster  cantidad_de_palabras_clave  porcentaje_de_palabras_clave
        0        1                         105                          15.9
        1        2                         102                          15.4
        ...
    """

    # Una línea de inicio de clúster: número, cantidad, porcentaje y primer trozo de texto
    inicio = re.compile(r"^\s*(\d+)\s+(\d+)\s+(\d+,\d+)\s*%\s*(.*)$")

    with open("data/clusters_report.txt", encoding="utf-8") as archivo:
        lineas = archivo.read().splitlines()

    grupos = []
    for linea in lineas:
        m = inicio.match(linea)
        if m:
            numero, cantidad, porcentaje, texto = m.groups()
            grupos.append([int(numero), int(cantidad), float(porcentaje.replace(",", ".")), [texto]])
        elif grupos and linea.strip() and not linea.lstrip().startswith("-"):
            # Línea de continuación: se pega al clúster anterior
            grupos[-1][3].append(linea)

    filas = []
    for numero, cantidad, porcentaje, trozos in grupos:
        # Se juntan los trozos y se colapsan los espacios repetidos de la alineación
        texto = " ".join(" ".join(trozos).split())
        # Cada clúster termina con un punto que no hace parte de la palabra clave
        filas.append((numero, cantidad, porcentaje, texto.removesuffix(".")))

    return pd.DataFrame(
        filas,
        columns=[
            "cluster",
            "cantidad_de_palabras_clave",
            "porcentaje_de_palabras_clave",
            "principales_palabras_clave",
        ],
    )
