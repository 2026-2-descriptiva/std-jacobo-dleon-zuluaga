import json
from pathlib import Path

import numpy as np
import pandas as pd

K = 5
QI_ORIGINAL = ["age", "sex", "bmi", "children", "region"]
ESQUEMAS = {
    "with_children": ["age_group", "sex", "bmi_group", "children_group", "region"],
    "without_children": ["age_group", "sex", "bmi_group", "region"],
}


def _agregar_grupos(df):
    # los intervalos de age y children cierran a la derecha; los de bmi a la izquierda
    df["age_group"] = pd.cut(
        df["age"], bins=[0, 29, 39, 49, np.inf], labels=["18-29", "30-39", "40-49", "50-64"]
    ).astype(str)
    df["bmi_group"] = pd.cut(
        df["bmi"],
        bins=[0, 18.5, 25, 30, np.inf],
        right=False,
        labels=["bajo peso", "normal", "sobrepeso", "obesidad"],
    ).astype(str)
    df["children_group"] = pd.cut(
        df["children"], bins=[-1, 0, 2, np.inf], labels=["0", "1-2", "3+"]
    ).astype(str)
    return df


def _evaluar_esquema(df, qi):
    """Devuelve el resumen del esquema y los registros que se publican."""
    tamanos = df.groupby(qi)["age"].transform("size")
    publicados = df[tamanos >= K]

    # una clase sin diversidad tiene un solo valor distinto de smoker
    valores_smoker = publicados.groupby(qi)["smoker"].nunique()
    clases_sin_diversidad = valores_smoker[valores_smoker == 1]
    filas_sin_diversidad = publicados.groupby(qi)["smoker"].transform("nunique").eq(1).sum()

    resumen = {
        "quasi_identifiers": qi,
        "equivalence_classes": int(df.groupby(qi).ngroups),
        "k_before_suppression": int(tamanos.min()),
        "suppressed_records": int(len(df) - len(publicados)),
        "published_records": int(len(publicados)),
        "published_classes": int(publicados.groupby(qi).ngroups),
        "classes_without_smoker_diversity": int(len(clases_sin_diversidad)),
        "records_without_smoker_diversity": int(filas_sin_diversidad),
    }
    return resumen, publicados


def pregunta_01():
    """
    Una aseguradora quiere publicar datos de sus afiliados para que un grupo
    de investigación estudie el costo de los seguros, sin que nadie pueda
    reconocer a una persona. El archivo `data/insurance.csv.gz` tiene una fila
    por afiliado con su edad (`age`), sexo (`sex`), índice de masa corporal
    (`bmi`), número de hijos (`children`), si fuma (`smoker`), región
    (`region`) y el costo de su seguro (`charges`).

    El archivo no tiene nombres ni documentos, pero eso no basta: la edad, el
    sexo, el índice de masa corporal, el número de hijos y la región son
    cuasi-identificadores, porque combinados pueden señalar a una persona.
    `smoker` es el atributo sensible que se quiere proteger.

    En este laboratorio usted va a medir el riesgo de reidentificación y a
    decidir qué publicar. Use estas definiciones:

    - Una clase de equivalencia es un grupo de registros con los mismos
      valores en todos los cuasi-identificadores. Un conjunto de datos cumple
      k-anonimato si toda clase tiene al menos k registros. Use k = 5.
    - `age_group`: `18-29`, `30-39`, `40-49` o `50-64`.
    - `bmi_group`: `bajo peso` (menos de 18.5), `normal` (desde 18.5 y menos
      de 25), `sobrepeso` (desde 25 y menos de 30) u `obesidad` (30 o más).
    - `children_group`: `0`, `1-2` o `3+`.

    Evalúe dos esquemas de generalización:

    - `with_children`: `age_group`, `sex`, `bmi_group`, `children_group` y
      `region`.
    - `without_children`: `age_group`, `sex`, `bmi_group` y `region`; el
      número de hijos no se publica.

    En cada esquema, suprima (no publique) los registros de las clases con
    menos de 5 registros. Luego, entre las clases publicadas, identifique las
    que no tienen diversidad en el atributo sensible, es decir, aquellas en
    las que todos los afiliados fuman o ninguno fuma: en esas clases, saber
    que alguien pertenece a ellas revela si fuma.

    Escriba `submission/privacy_report.json` con estas claves:

    - `original_k`: el menor tamaño de clase usando los cuasi-identificadores
      originales, sin generalizar.
    - `original_unique_records`: cuántos registros son los únicos de su clase
      con los cuasi-identificadores originales.
    - `schemes`: un diccionario con una entrada por esquema (`with_children` y
      `without_children`), cada una con las claves `quasi_identifiers` (la
      lista de columnas del esquema), `equivalence_classes` (clases antes de
      suprimir), `k_before_suppression`, `suppressed_records`,
      `published_records`, `published_classes`,
      `classes_without_smoker_diversity` y
      `records_without_smoker_diversity`.
    - `selected_scheme`: el esquema que suprime menos registros.
    - `mean_charges_original` y `mean_charges_published`: el costo promedio
      de todos los afiliados y el de los registros publicados con el esquema
      seleccionado.
    - `smoker_rate_original` y `smoker_rate_published`: la proporción de
      fumadores en ambos casos.

    Escriba también `submission/insurance_published.csv`, sin el índice de
    Pandas, con los registros publicados del esquema seleccionado, en el
    mismo orden del archivo original, y las columnas del esquema seguidas de
    `smoker` y `charges`.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "original_k": 1,
          "original_unique_records": 1330,
          "schemes": {
            "with_children": {
              "quasi_identifiers": ["age_group", "sex", ...],
              "equivalence_classes": 278,
              ...
            },
            ...
          },
          ...
        }
    """

    Path("submission").mkdir(exist_ok=True)

    df = _agregar_grupos(pd.read_csv("data/insurance.csv.gz"))

    # riesgo de partida, con los valores sin generalizar
    tam_original = df.groupby(QI_ORIGINAL)["age"].transform("size")

    resumenes = {}
    publicados_por_esquema = {}
    for nombre, qi in ESQUEMAS.items():
        resumenes[nombre], publicados_por_esquema[nombre] = _evaluar_esquema(df, qi)

    # si empatan gana without_children, que publica una columna menos
    elegido = min(
        ["without_children", "with_children"],
        key=lambda n: resumenes[n]["suppressed_records"],
    )
    pub = publicados_por_esquema[elegido]

    reporte = {
        "original_k": int(tam_original.min()),
        "original_unique_records": int((tam_original == 1).sum()),
        "schemes": resumenes,
        "selected_scheme": elegido,
        "mean_charges_original": round(float(df["charges"].mean()), 4),
        "mean_charges_published": round(float(pub["charges"].mean()), 4),
        "smoker_rate_original": round(float((df["smoker"] == "yes").mean()), 4),
        "smoker_rate_published": round(float((pub["smoker"] == "yes").mean()), 4),
    }

    with open("submission/privacy_report.json", "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)

    # las filas ya conservan el orden del archivo original
    columnas = ESQUEMAS[elegido] + ["smoker", "charges"]
    pub[columnas].to_csv("submission/insurance_published.csv", index=False)

    return reporte
