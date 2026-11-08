import gzip


def pregunta_01():
    """
    Calcule la suma de los valores de la segunda columna (`value`) del
    archivo `data/data.csv.gz` y retorne el resultado como un número entero.

    Ejemplo del formato de la respuesta:

        214
    """
    total = 0
    with gzip.open("data/data.csv.gz", "rt") as archivo:
        for linea in archivo:
            columnas = linea.rstrip("\n").split("\t")
            total += int(columnas[1])
    return total
