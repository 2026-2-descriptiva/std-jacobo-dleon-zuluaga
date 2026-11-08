import pandas as pd


def pregunta_03():
    """
    Usando `data/tbl0.tsv`, cuente cuántos registros hay para cada categoría
    de la columna `c1`. Retorne una Serie de Pandas cuyo índice son las
    categorías, en orden alfabético, y cuyos valores son las cantidades.

    Ejemplo del formato de la respuesta:

        c1
        A     8
        B     7
        C     5
        ...
    """
    tabla = pd.read_csv("data/tbl0.tsv", sep="\t")
    conteo = tabla["c1"].value_counts()
    # value_counts ordena por frecuencia; se pide orden alfabético del índice
    return conteo.sort_index()
