import gzip


def pregunta_03():
    """
    Sume los valores de la segunda columna (`value`) para cada letra de la
    primera columna (`letter`). Retorne una lista de tuplas `(letra, suma)`
    ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 53), ("B", 36), ("C", 27), ...]
    """
    sumas = {}
    with gzip.open("data/data.csv.gz", "rt") as archivo:
        for linea in archivo:
            letra, valor = linea.split("\t")[:2]
            sumas[letra] = sumas.get(letra, 0) + int(valor)
    return sorted(sumas.items())
