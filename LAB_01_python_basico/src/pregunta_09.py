import gzip


def pregunta_09():
    """
    Cuente cuántas veces aparece cada clave en la quinta columna (`metrics`)
    de todo el archivo. Retorne un diccionario `{clave: cantidad}` con las
    claves en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"aaa": 13, "bbb": 16, "ccc": 23, ...}
    """
    veces = {}
    with gzip.open("data/data.csv.gz", "rt") as archivo:
        for linea in archivo:
            metricas = linea.rstrip("\n").split("\t")[4]
            for par in metricas.split(","):
                clave = par.split(":")[0]
                veces[clave] = veces.get(clave, 0) + 1
    return {clave: veces[clave] for clave in sorted(veces)}
