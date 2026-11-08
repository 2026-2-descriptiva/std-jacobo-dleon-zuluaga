import gzip


def pregunta_06():
    """
    La quinta columna (`metrics`) contiene pares `clave:valor` separados por
    comas. Para cada clave, encuentre el valor mínimo y el valor máximo que
    aparecen en todo el archivo. Retorne una lista de tuplas
    `(clave, mínimo, máximo)` ordenada alfabéticamente por la clave.

    Observe que el orden es mínimo y luego máximo, al contrario de la
    pregunta 5.

    Ejemplo del formato de la respuesta:

        [("aaa", 1, 9), ("bbb", 1, 9), ...]
    """
    valores_por_clave = {}
    with gzip.open("data/data.csv.gz", "rt") as archivo:
        for linea in archivo:
            metricas = linea.rstrip("\n").split("\t")[4]
            for par in metricas.split(","):
                clave, numero = par.split(":")
                valores_por_clave.setdefault(clave, []).append(int(numero))
    # aquí el orden pedido es (clave, mínimo, máximo)
    return [
        (clave, min(nums), max(nums))
        for clave, nums in sorted(valores_por_clave.items())
    ]
