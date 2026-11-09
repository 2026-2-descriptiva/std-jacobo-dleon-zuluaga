import os

import pandas as pd


COLUMNAS = [
    "sexo",
    "tipo_de_emprendimiento",
    "idea_negocio",
    "barrio",
    "estrato",
    "comuna_ciudadano",
    "fecha_de_beneficio",
    "monto_del_credito",
    "línea_credito",
]
COLUMNAS_TEXTO = ["sexo", "tipo_de_emprendimiento", "idea_negocio", "barrio", "línea_credito"]
FORMATOS_FECHA = ["%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d"]


def _limpiar_texto(serie):
    # los guiones reemplazan espacios en algunos registros ("fabrica-de-")
    serie = serie.str.lower().str.replace("-", " ", regex=False)
    # split + join deja un solo espacio entre palabras y quita los de los bordes
    return serie.str.split().str.join(" ")


def _leer_fechas(serie):
    # cada fecha cumple solo uno de los formatos, así que se prueba uno por uno
    fechas = pd.Series(pd.NaT, index=serie.index, dtype="datetime64[ns]")
    for formato in FORMATOS_FECHA:
        fechas = fechas.fillna(pd.to_datetime(serie, format=formato, errors="coerce"))
    return fechas


def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.

    Su tarea es limpiarlo y guardar el resultado en
    `submission/solicitudes_de_credito.csv`, usando punto y coma (`;`) como
    separador y sin el índice de Pandas.

    El archivo limpio debe cumplir lo siguiente:

    - Contiene solamente las nueve columnas `sexo`, `tipo_de_emprendimiento`,
      `idea_negocio`, `barrio`, `estrato`, `comuna_ciudadano`,
      `fecha_de_beneficio`, `monto_del_credito` y `línea_credito`, en ese
      orden.
    - Los campos de texto están en minúsculas y sus palabras separadas por
      espacios.
    - `estrato` y `monto_del_credito` son números enteros, sin símbolos ni
      separadores de miles.
    - Todas las fechas de `fecha_de_beneficio` usan un mismo formato, por
      ejemplo `AAAA-MM-DD`.
    - No hay registros incompletos. La única excepción es
      `comuna_ciudadano`: sus valores faltantes son parte de los datos
      originales y deben conservarse.
    - No hay registros duplicados.

    Ejemplo del formato del archivo:

        sexo;tipo_de_emprendimiento;idea_negocio;barrio;estrato;...
        femenino;comercio;almacen de ropa en;los cerros el vergel;2;...
        ...
    """

    os.makedirs("submission", exist_ok=True)

    df = pd.read_csv("data/solicitudes_de_credito.csv.gz", sep=";", dtype=str)
    # la primera columna es el índice viejo y no es un dato
    df = df.drop(columns=df.columns[0])

    for col in COLUMNAS_TEXTO:
        df[col] = _limpiar_texto(df[col])

    # "02" -> 2
    df["estrato"] = pd.to_numeric(df["estrato"].str.strip()).astype("Int64")

    # "$ 7,000,000.00" -> "7000000.00" -> 7000000
    monto = df["monto_del_credito"].str.replace(r"[^\d.]", "", regex=True)
    df["monto_del_credito"] = pd.to_numeric(monto).round().astype("Int64")

    df["fecha_de_beneficio"] = _leer_fechas(df["fecha_de_beneficio"].str.strip()).dt.strftime(
        "%Y-%m-%d"
    )
    # la comuna vacía es un dato real, por eso se deja fuera de la revisión de nulos
    df["comuna_ciudadano"] = pd.to_numeric(df["comuna_ciudadano"]).astype("Int64")

    obligatorias = [c for c in COLUMNAS if c != "comuna_ciudadano"]
    df = df.dropna(subset=obligatorias)
    # los duplicados se buscan al final, cuando ya todo tiene el mismo formato
    df = df.drop_duplicates()

    df["estrato"] = df["estrato"].astype(int)
    df["monto_del_credito"] = df["monto_del_credito"].astype(int)

    df[COLUMNAS].to_csv("submission/solicitudes_de_credito.csv", sep=";", index=False)
