import gzip


def pregunta_08():
    """
    Repita la pregunta 7, pero ahora cada lista de letras debe contener cada
    letra una sola vez y estar ordenada alfabéticamente. Retorne una lista de
    tuplas `(valor, letras)` ordenada por el valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["B", "E"]), (2, ["A", "E"]), ...]
    """
    letras_por_valor = {}
    with gzip.open("data/data.csv.gz", "rt") as archivo:
        for linea in archivo:
            letra, valor = linea.split("\t")[:2]
            letras_por_valor.setdefault(int(valor), set()).add(letra)
    resultado = []
    for valor in sorted(letras_por_valor):
        resultado.append((valor, sorted(letras_por_valor[valor])))
    return resultado
