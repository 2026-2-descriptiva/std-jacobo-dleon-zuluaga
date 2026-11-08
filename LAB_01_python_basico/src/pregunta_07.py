import gzip


def pregunta_07():
    """
    Para cada valor distinto de la segunda columna (`value`), construya la
    lista de letras de la primera columna (`letter`) que aparecen con ese
    valor. Conserve las letras repetidas y el orden en que aparecen en el
    archivo. Retorne una lista de tuplas `(valor, letras)` ordenada por el
    valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["E", "B", "E"]), (2, ["A", "E"]), ...]
    """
    letras_por_valor = {}
    with gzip.open("data/data.csv.gz", "rt") as archivo:
        for linea in archivo:
            letra, valor = linea.split("\t")[:2]
            letras_por_valor.setdefault(int(valor), []).append(letra)
    # la clave se guarda como int para que el orden sea numérico
    return sorted(letras_por_valor.items())
