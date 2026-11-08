import gzip


def pregunta_12():
    """
    Para cada letra de la primera columna (`letter`), sume todos los valores
    numéricos de los pares `clave:valor` de la quinta columna (`metrics`).
    Retorne un diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"A": 177, "B": 187, "C": 114, ...}
    """
    por_letra = {}
    with gzip.open("data/data.csv.gz", "rt") as archivo:
        for linea in archivo:
            columnas = linea.rstrip("\n").split("\t")
            letra = columnas[0]
            suma_fila = 0
            for par in columnas[4].split(","):
                suma_fila += int(par.split(":")[1])
            por_letra[letra] = por_letra.get(letra, 0) + suma_fila
    return dict(sorted(por_letra.items()))
