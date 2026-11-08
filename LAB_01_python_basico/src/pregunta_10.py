import gzip


def pregunta_10():
    """
    Para cada registro del archivo, en el mismo orden en que aparecen,
    retorne una tupla con la letra de la primera columna (`letter`), la
    cantidad de elementos de la cuarta columna (`codes`) y la cantidad de
    pares de la quinta columna (`metrics`). El resultado es una lista con una
    tupla por registro.

    Ejemplo del formato de la respuesta:

        [("E", 3, 5), ("A", 3, 4), ("B", 4, 4), ...]
    """
    filas = []
    with gzip.open("data/data.csv.gz", "rt") as archivo:
        for linea in archivo:
            columnas = linea.rstrip("\n").split("\t")
            n_codigos = len(columnas[3].split(","))
            n_pares = len(columnas[4].split(","))
            filas.append((columnas[0], n_codigos, n_pares))
    return filas
