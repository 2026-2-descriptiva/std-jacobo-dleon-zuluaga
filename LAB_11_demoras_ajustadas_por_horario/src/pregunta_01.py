from pathlib import Path

import pandas as pd

RUTA_DATOS = Path("data") / "flights_by_carrier_day_hour.csv.gz"
CARPETA_SALIDA = Path("submission")
MIN_VUELOS = 100_000


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Una autoridad aeronáutica publica cada año un ranking de aerolíneas según
    su tasa de demora, y algunas aerolíneas se quejan de que es injusto: las
    demoras se acumulan a lo largo del día, de modo que una aerolínea con
    muchos vuelos en la tarde y la noche parece peor aunque opere igual de
    bien que las demás. Su tarea es construir un ranking que tenga en cuenta
    la mezcla de horarios de cada aerolínea.

    El archivo `data/flights_by_carrier_day_hour.csv.gz` tiene los vuelos
    nacionales entre 2006 y 2008, agregados por año, mes, día de la semana,
    hora programada de salida (`scheduled_departure_hour`) y aerolínea
    (`reporting_airline`). Use las columnas `operated_flights` (vuelos
    operados) y `delayed_departure_15_flights` (vuelos que salieron con 15
    minutos o más de demora).

    Siga estos pasos:

    1. Calcule la tasa nacional de demora de cada hora programada de salida:
       vuelos demorados sobre vuelos operados, con todas las aerolíneas
       juntas.
    2. Para cada aerolínea, calcule las demoras esperadas: en cada hora,
       multiplique sus vuelos operados por la tasa nacional de esa hora, y
       sume sobre todas las horas. Son las demoras que tendría si en cada hora
       se comportara como el promedio nacional.
    3. Divida las demoras observadas entre las esperadas. Un valor mayor que 1
       significa que la aerolínea se demora más de lo que explican sus
       horarios.

    Genere dos archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `hourly_delay_rates.csv`, con una fila por hora, de 0 a 23:
       `scheduled_departure_hour`, `operated_flights`,
       `delayed_departure_15_flights` y `delay_rate`.

    2. `carrier_adjusted_delays.csv`, con una fila por aerolínea:
       `reporting_airline`, `operated_flights`,
       `delayed_departure_15_flights`, `delay_rate` (la tasa sin ajustar),
       `expected_delayed_flights`, `observed_to_expected_ratio`, `crude_rank`
       y `adjusted_rank`. Incluya solamente aerolíneas con al menos 100 000
       vuelos operados. `crude_rank` es la posición según `delay_rate` y
       `adjusted_rank` la posición según `observed_to_expected_ratio`; en
       ambos, 1 es la peor aerolínea. Ordene la tabla por `adjusted_rank`.

    Compare los dos rankings: las aerolíneas que cambian de posición son las
    que el ranking sin ajustar juzga mal por sus horarios.

    La función también debe retornar las dos tablas, en el mismo orden.

    Ejemplo del formato de `carrier_adjusted_delays.csv`:

        reporting_airline,operated_flights,...,crude_rank,adjusted_rank
        EV,819223,...,1,1
        ...
    """

    CARPETA_SALIDA.mkdir(exist_ok=True)

    vuelos = pd.read_csv(RUTA_DATOS)
    columnas = ["operated_flights", "delayed_departure_15_flights"]

    # tasa nacional por hora (todas las aerolineas juntas)
    por_hora = vuelos.groupby("scheduled_departure_hour")[columnas].sum()
    tasa_hora = por_hora["delayed_departure_15_flights"] / por_hora["operated_flights"]

    horas = por_hora.reset_index()
    horas[columnas] = horas[columnas].astype(int)
    horas["delay_rate"] = tasa_hora.round(4).to_numpy()

    # vuelos de cada aerolinea en cada hora, con la tasa nacional de esa hora al lado
    aero_hora = (
        vuelos.groupby(["reporting_airline", "scheduled_departure_hour"])[
            "operated_flights"
        ]
        .sum()
        .reset_index()
    )
    aero_hora["tasa_nacional"] = aero_hora["scheduled_departure_hour"].map(tasa_hora)
    # demoras que tendria la aerolinea si en cada hora fuera como el promedio
    aero_hora["esperadas"] = aero_hora["operated_flights"] * aero_hora["tasa_nacional"]
    esperadas = aero_hora.groupby("reporting_airline")["esperadas"].sum()

    aerolineas = vuelos.groupby("reporting_airline")[columnas].sum()
    aerolineas = aerolineas[aerolineas["operated_flights"] >= MIN_VUELOS].copy()
    aerolineas["delay_rate"] = (
        aerolineas["delayed_departure_15_flights"] / aerolineas["operated_flights"]
    )
    aerolineas["expected_delayed_flights"] = esperadas.reindex(aerolineas.index)
    aerolineas["observed_to_expected_ratio"] = (
        aerolineas["delayed_departure_15_flights"]
        / aerolineas["expected_delayed_flights"]
    )

    # puesto 1 = peor aerolinea (mayor tasa o mayor razon)
    aerolineas["crude_rank"] = (
        aerolineas["delay_rate"].rank(ascending=False, method="first").astype(int)
    )
    aerolineas["adjusted_rank"] = (
        aerolineas["observed_to_expected_ratio"]
        .rank(ascending=False, method="first")
        .astype(int)
    )

    aerolineas[columnas] = aerolineas[columnas].astype(int)
    aerolineas = (
        aerolineas.round(
            {
                "delay_rate": 4,
                "expected_delayed_flights": 4,
                "observed_to_expected_ratio": 4,
            }
        )
        .sort_values("adjusted_rank")
        .reset_index()
    )

    horas.to_csv(CARPETA_SALIDA / "hourly_delay_rates.csv", index=False)
    aerolineas.to_csv(CARPETA_SALIDA / "carrier_adjusted_delays.csv", index=False)

    return horas, aerolineas
