from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def build_cohort_analysis() -> pd.DataFrame:
    """
    Una tienda quiere saber si sus clientes vuelven a comprar después de su
    primera compra. Para responder, agrupe a los clientes en cohortes según
    el mes de su primera compra y mida, mes a mes, qué proporción de cada
    cohorte vuelve a comprar. Use `data/sales.csv.gz`, que tiene una fila por
    orden con su cliente (`CustomerID`) y su fecha (`OrderDate`).

    Use estas definiciones:

    - `cohort_month`: el mes de la primera compra del cliente, escrito como
      `AAAA-MM`.
    - `period_index`: los meses transcurridos desde `cohort_month`; es 0 en el
      mes de la primera compra, 1 en el mes siguiente, y así sucesivamente.
    - `active_customers`: la cantidad de clientes distintos de la cohorte que
      compraron en ese período.
    - `cohort_size`: la cantidad de clientes de la cohorte, es decir, sus
      clientes activos en el período 0.
    - `retention_rate`: `active_customers` sobre `cohort_size`.

    Genere dos archivos en `submission/`:

    1. `cohort_retention.csv`, sin el índice de Pandas, con las columnas
       `cohort_month`, `period_index`, `active_customers`, `cohort_size` y
       `retention_rate`, y una fila por cada combinación cohorte–período
       observada, ordenadas por cohorte y período.

    2. `cohort_retention_heatmap.png`, un mapa de calor de `retention_rate`
       con una fila por cohorte (eje vertical) y una columna por período
       (eje horizontal). Muestre los valores como porcentajes. Los períodos
       que todavía no se pueden observar para una cohorte no significan
       retención cero: déjelos vacíos en el mapa.

    La función también debe retornar la tabla de retención.

    Ejemplo del formato de `cohort_retention.csv`:

        cohort_month,period_index,active_customers,cohort_size,retention_rate
        2022-01,0,100,100,1.0
        2022-01,1,26,100,0.26
        ...
    """

    carpeta_salida = Path("submission")
    carpeta_salida.mkdir(exist_ok=True)

    ordenes = pd.read_csv("data/sales.csv.gz", parse_dates=["OrderDate"])

    # mes calendario de cada orden, como número absoluto para poder restar
    ordenes["mes_orden"] = ordenes["OrderDate"].dt.year * 12 + ordenes["OrderDate"].dt.month
    primer_mes = ordenes.groupby("CustomerID")["mes_orden"].transform("min")
    ordenes["period_index"] = ordenes["mes_orden"] - primer_mes

    # la cohorte es el mes de la primera compra, en formato AAAA-MM
    anio, mes = divmod(primer_mes - 1, 12)
    ordenes["cohort_month"] = anio.astype(str) + "-" + (mes + 1).astype(str).str.zfill(2)

    # un cliente cuenta una sola vez por período aunque haya hecho varias órdenes
    retencion = (
        ordenes.groupby(["cohort_month", "period_index"], as_index=False)
        .agg(active_customers=("CustomerID", "nunique"))
    )

    # tamaño de la cohorte = activos en el período 0
    tam_cohorte = retencion.loc[retencion["period_index"] == 0].set_index("cohort_month")["active_customers"]
    retencion["cohort_size"] = retencion["cohort_month"].map(tam_cohorte)
    retencion["retention_rate"] = retencion["active_customers"] / retencion["cohort_size"]
    retencion = retencion.sort_values(["cohort_month", "period_index"], ignore_index=True)

    retencion.to_csv(carpeta_salida / "cohort_retention.csv", index=False)

    # matriz cohorte x período; lo que no se observó queda como NaN (vacío)
    matriz = retencion.pivot(index="cohort_month", columns="period_index", values="retention_rate")

    fig, ax = plt.subplots(figsize=(9, 5))
    imagen = ax.imshow(matriz.to_numpy(), cmap="Blues", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(matriz.shape[1]), labels=matriz.columns)
    ax.set_yticks(range(matriz.shape[0]), labels=matriz.index)
    ax.set_xlabel("period_index (meses desde la primera compra)")
    ax.set_ylabel("cohort_month")
    ax.set_title("Retención por cohorte")

    for i in range(matriz.shape[0]):
        for j in range(matriz.shape[1]):
            valor = matriz.iat[i, j]
            if pd.notna(valor):
                color = "white" if valor > 0.6 else "black"
                ax.text(j, i, f"{valor:.0%}", ha="center", va="center", fontsize=8, color=color)

    fig.colorbar(imagen, ax=ax, label="retention_rate")
    fig.tight_layout()
    fig.savefig(carpeta_salida / "cohort_retention_heatmap.png", dpi=120)
    plt.close(fig)

    return retencion
