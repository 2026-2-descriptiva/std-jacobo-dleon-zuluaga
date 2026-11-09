from pathlib import Path

import pandas as pd

RUTA_DATOS = Path("data") / "superstore_orders.csv.gz"
CARPETA_SALIDA = Path("submission")

# limites superiores de cada rango (el primero es solo el cero exacto)
LIMITES = [-1, 0, 0.05, 0.10, float("inf")]
RANGOS = ["0%", "1%-5%", "6%-10%", "más de 10%"]


def _indicadores(grupos):
    """Agrega ventas y utilidad por grupo y calcula margen y tasa de perdida."""
    tabla = grupos.agg(
        lines=("Profit", "size"),
        sales=("Sales", "sum"),
        profit=("Profit", "sum"),
        lineas_perdida=("hay_perdida", "sum"),
        lost_profit=("monto_perdido", "sum"),
    )
    tabla["profit_margin"] = tabla["profit"] / tabla["sales"]
    tabla["loss_line_rate"] = tabla["lineas_perdida"] / tabla["lines"]
    return tabla


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una cadena de suministros de oficina vende mucho, pero la gerencia
    sospecha que parte de esas ventas no deja utilidad. El archivo
    `data/superstore_orders.csv.gz` tiene una fila por línea de pedido, con
    el número de pedido (`Order ID`), las ventas (`Sales`), la utilidad
    (`Profit`), el descuento aplicado (`Discount`, como proporción), el
    segmento del cliente (`Customer Segment`) y la categoría del producto
    (`Product Category`). Una utilidad negativa significa que la línea se
    vendió con pérdida.

    Use estas definiciones:

    - Margen (`profit_margin`): utilidad sobre ventas.
    - Línea con pérdida: una línea cuya utilidad es negativa.
    - `loss_line_rate`: la proporción de líneas con pérdida.
    - `lost_profit`: la suma de las pérdidas de las líneas con pérdida,
      escrita como número positivo.
    - Rango de descuento (`discount_band`): `0%` si no hubo descuento,
      `1%-5%` si fue mayor que 0 y hasta 5 %, `6%-10%` si fue mayor que 5 % y
      hasta 10 %, y `más de 10%` en otro caso.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `profitability_summary.csv`, con una sola fila: `lines` (cantidad de
       líneas), `orders` (pedidos distintos), `sales`, `profit`,
       `profit_margin`, `loss_lines` (cantidad de líneas con pérdida),
       `loss_line_rate` y `lost_profit`.

    2. `discount_summary.csv`, con una fila por rango de descuento, en el
       orden en que se definieron arriba: `discount_band`, `lines`, `sales`,
       `profit`, `profit_margin`, `loss_line_rate` y `lost_profit`.

    3. `priority_segments.csv`, con los cinco segmentos segmento–categoría
       que más utilidad pierden: `Customer Segment`, `Product Category`,
       `lines`, `sales`, `profit`, `profit_margin` y `lost_profit`. Considere
       solamente segmentos con al menos 100 líneas y ordénelos por
       `lost_profit` de mayor a menor.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `discount_summary.csv`:

        discount_band,lines,sales,profit,profit_margin,loss_line_rate,...
        0%,166,170539.05,29472.3789,0.1728,0.488,...
        ...
    """

    CARPETA_SALIDA.mkdir(exist_ok=True)

    # el archivo usa ; como separador y coma decimal
    lineas = pd.read_csv(RUTA_DATOS, sep=";", decimal=",")

    # dos columnas auxiliares para no repetir el filtro de utilidad negativa
    lineas["hay_perdida"] = lineas["Profit"] < 0
    lineas["monto_perdido"] = (-lineas["Profit"]).where(lineas["hay_perdida"], 0.0)

    # resumen general: una sola fila
    total_ventas = lineas["Sales"].sum()
    total_utilidad = lineas["Profit"].sum()
    n_lineas = len(lineas)
    n_perdida = int(lineas["hay_perdida"].sum())
    resumen = pd.DataFrame(
        {
            "lines": [n_lineas],
            "orders": [lineas["Order ID"].nunique()],
            "sales": [total_ventas],
            "profit": [total_utilidad],
            "profit_margin": [total_utilidad / total_ventas],
            "loss_lines": [n_perdida],
            "loss_line_rate": [n_perdida / n_lineas],
            "lost_profit": [lineas["monto_perdido"].sum()],
        }
    )

    # rangos de descuento; pd.cut incluye el limite derecho de cada intervalo
    lineas["discount_band"] = pd.cut(
        lineas["Discount"], bins=LIMITES, labels=RANGOS, right=True
    )
    por_descuento = _indicadores(lineas.groupby("discount_band", observed=False))
    descuentos = por_descuento.reset_index()[
        [
            "discount_band",
            "lines",
            "sales",
            "profit",
            "profit_margin",
            "loss_line_rate",
            "lost_profit",
        ]
    ]

    # segmentos con al menos 100 lineas, los 5 que mas utilidad pierden
    por_segmento = _indicadores(
        lineas.groupby(["Customer Segment", "Product Category"])
    ).reset_index()
    prioritarios = (
        por_segmento[por_segmento["lines"] >= 100]
        .sort_values("lost_profit", ascending=False)
        .head(5)[
            [
                "Customer Segment",
                "Product Category",
                "lines",
                "sales",
                "profit",
                "profit_margin",
                "lost_profit",
            ]
        ]
        .reset_index(drop=True)
    )

    resumen.to_csv(CARPETA_SALIDA / "profitability_summary.csv", index=False)
    descuentos.to_csv(CARPETA_SALIDA / "discount_summary.csv", index=False)
    prioritarios.to_csv(CARPETA_SALIDA / "priority_segments.csv", index=False)

    return resumen, descuentos, prioritarios
