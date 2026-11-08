import gzip
from collections import defaultdict


def pregunta_04():
    """
    Cuente cuántos registros hay en cada mes, usando la fecha de la tercera
    columna (`date`). Represente el mes como un texto de dos dígitos y retorne
    una lista de tuplas `(mes, cantidad)` ordenada por el mes.

    Ejemplo del formato de la respuesta:

        [("01", 3), ("02", 4), ("03", 2), ...]
    """
    por_mes = defaultdict(int)
    with gzip.open("data/data.csv.gz", "rt") as archivo:
        for linea in archivo:
            fecha = linea.split("\t")[2]
            # formato YYYY-MM-DD: el mes queda entre los guiones
            mes = fecha.split("-")[1]
            por_mes[mes] += 1
    return sorted(por_mes.items())
