import json
from pathlib import Path

import pandas as pd

COLUMNAS_REQUERIDAS = [
    "supplier_id",
    "supplier",
    "country",
    "city",
    "purchase_date",
    "amount",
    "discount",
    "weight",
    "units",
    "unit_price",
    "contact_email",
]


def main():
    """
    Antes de limpiar o analizar un conjunto de datos, un analista debe
    documentar qué problemas tiene. En este laboratorio usted no va a limpiar
    `data/ventas.csv.gz`: va a construir un reporte de calidad que deje evidencia
    de sus problemas, tal como están en el archivo.

    Lea `data/ventas.csv.gz` sin modificar sus valores. Para trabajar con los
    encabezados, normalícelos: páselos a minúsculas, elimine los espacios al
    inicio y al final (y cualquier marca BOM) y reemplace los espacios
    internos por `_`. Las columnas requeridas son `supplier_id`, `supplier`,
    `country`, `city`, `purchase_date`, `amount`, `discount`, `weight`,
    `units`, `unit_price` y `contact_email`.

    Escriba el reporte en `submission/data_quality_report.json` con estas
    claves:

    - `row_count`: cantidad de filas de datos.
    - `column_count`: cantidad de columnas.
    - `missing_required_columns`: lista ordenada de columnas requeridas que no
      están en el archivo.
    - `unexpected_columns`: lista ordenada de columnas del archivo que no son
      requeridas.
    - `duplicate_row_count`: cantidad de filas idénticas a una fila anterior.
    - `duplicate_supplier_id_row_count`: cantidad de filas cuyo `supplier_id`
      aparece más de una vez (cuente todas esas filas, no solo las
      repetidas).
    - `missing_value_count_by_column`: diccionario con la cantidad de valores
      faltantes de cada columna. Considere faltantes las celdas vacías y las
      que contienen `N/A`.
    - `invalid_email_count`: cantidad de valores de `contact_email` que no
      tienen la forma `usuario@dominio.extension`.
    - `invalid_unit_count`: cantidad de valores numéricos de `units` que no son
      enteros positivos. Los valores faltantes no se cuentan aquí.
    - `country_values`: lista ordenada de los valores distintos de `country`,
      escritos exactamente como aparecen en el archivo.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "row_count": 103,
          "column_count": 11,
          "missing_required_columns": [],
          ...
          "country_values": [" Colombia ", "CO", ...]
        }
    """

    # Todo se lee como texto para no alterar ningún valor (ceros a la izquierda,
    # formatos de fecha, etc.). Solo se marcan como faltantes "" y "N/A".
    # utf-8-sig quita la marca BOM del primer encabezado.
    ventas = pd.read_csv(
        "data/ventas.csv.gz",
        dtype=str,
        encoding="utf-8-sig",
        keep_default_na=False,
        na_values=["", "N/A"],
    )
    ventas.columns = [
        nombre.replace("\ufeff", "").strip().lower().replace(" ", "_")
        for nombre in ventas.columns
    ]

    columnas = list(ventas.columns)
    faltantes_requeridas = sorted(set(COLUMNAS_REQUERIDAS) - set(columnas))
    inesperadas = sorted(set(columnas) - set(COLUMNAS_REQUERIDAS))

    filas_duplicadas = int(ventas.duplicated().sum())
    # keep=False marca todas las filas del grupo, no solo las repetidas
    ids_repetidos = int(ventas["supplier_id"].duplicated(keep=False).sum())

    nulos_por_columna = ventas.isna().sum().astype(int).to_dict()

    # Los faltantes no se evalúan: solo se revisan los correos que sí vienen
    correos = ventas["contact_email"].dropna().str.strip()
    correos_invalidos = int((~correos.str.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+")).sum())

    # Lo que no se puede convertir a número queda como NaN y no se cuenta
    unidades = pd.to_numeric(ventas["units"], errors="coerce").dropna()
    es_entero_positivo = (unidades > 0) & (unidades % 1 == 0)
    unidades_invalidas = int((~es_entero_positivo).sum())

    # Se dejan los valores tal cual, con espacios y mayúsculas, porque justo eso es lo que se reporta
    paises = sorted(ventas["country"].dropna().unique())

    reporte = {
        "row_count": len(ventas),
        "column_count": len(columnas),
        "missing_required_columns": faltantes_requeridas,
        "unexpected_columns": inesperadas,
        "duplicate_row_count": filas_duplicadas,
        "duplicate_supplier_id_row_count": ids_repetidos,
        "missing_value_count_by_column": nulos_por_columna,
        "invalid_email_count": correos_invalidos,
        "invalid_unit_count": unidades_invalidas,
        "country_values": paises,
    }

    ruta = Path("submission") / "data_quality_report.json"
    ruta.parent.mkdir(exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(reporte, archivo, indent=2, ensure_ascii=False)

    return reporte
