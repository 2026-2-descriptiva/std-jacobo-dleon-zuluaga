import gzip


def pregunta_05():
    """
    Para cada letra de la primera columna (`letter`), encuentre el valor
    máximo y el valor mínimo de la segunda columna (`value`). Retorne una lista
    de tuplas `(letra, máximo, mínimo)` ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 9, 2), ("B", 9, 1), ...]
    """
    extremos = {}
    with gzip.open("data/data.csv.gz", "rt") as archivo:
        for linea in archivo:
            letra, valor = linea.split("\t")[:2]
            valor = int(valor)
            if letra not in extremos:
                extremos[letra] = [valor, valor]
            else:
                actual = extremos[letra]
                actual[0] = max(actual[0], valor)
                actual[1] = min(actual[1], valor)
    return [(letra, mx, mn) for letra, (mx, mn) in sorted(extremos.items())]
