import gzip
from collections import Counter


def pregunta_11():
    """
    La cuarta columna (`codes`) contiene letras minúsculas separadas por
    comas. Para cada una de esas letras, sume los valores de la segunda
    columna (`value`) de los registros en los que aparece. Retorne un
    diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"a": 122, "b": 49, "c": 91, ...}
    """
    acumulado = Counter()
    with gzip.open("data/data.csv.gz", "rt") as archivo:
        for linea in archivo:
            columnas = linea.rstrip("\n").split("\t")
            valor = int(columnas[1])
            # cada letra de codes recibe el valor completo del registro
            for codigo in columnas[3].split(","):
                acumulado[codigo] += valor
    return dict(sorted(acumulado.items()))
