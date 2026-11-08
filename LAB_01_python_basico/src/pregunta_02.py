import gzip
from collections import Counter


def pregunta_02():
    """
    Cuente cuántos registros hay para cada letra de la primera columna
    (`letter`). Retorne una lista de tuplas `(letra, cantidad)` ordenada
    alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 8), ("B", 7), ("C", 5), ...]
    """
    conteo = Counter()
    with gzip.open("data/data.csv.gz", "rt") as archivo:
        for linea in archivo:
            letra = linea.split("\t")[0]
            conteo[letra] += 1
    # sorted sobre las tuplas ordena por letra
    return sorted(conteo.items())
