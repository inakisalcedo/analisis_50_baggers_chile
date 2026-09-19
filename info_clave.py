import yfinance as yf
import pandas as pd
import numpy as np


ARCHIVO_ENTRADA = "universo_definitivo.xlsx"
ARCHIVO_SALIDA = "universo_definitivo_completo.xlsx"


def CAGR(valor_inicial, valor_final, años):
    """
    Calcula CAGR.
    Devuelve NaN si los datos no permiten calcularlo.
    """
    if pd.isna(valor_inicial) or pd.isna(valor_final):
        return np.nan

    if valor_inicial <= 0 or valor_final <= 0 or años <= 0:
        return np.nan

    return (valor_final / valor_inicial) ** (1 / años) - 1


def crecimiento_porcentual(valor_inicial, valor_final):
    """
    Crecimiento porcentual simple.
    """
    if pd.isna(valor_inicial) or pd.isna(valor_final):
        return np.nan

    if valor_inicial == 0:
        return np.nan

    return valor_final / valor_inicial - 1


def obtener_datos(symbol):

    try:

        print(f"Procesando {symbol}...")

        ticker = yf.Ticker(symbol)

        # ==========================================================
        # HISTORIAL DE PRECIOS Y DIVIDENDOS
        # ==========================================================

        historial = ticker.history(
            period="max",
            interval="1d",
            auto_adjust=False,
            actions=True
        )

        if historial.empty:
            print(f"  Sin historial para {symbol}")
            return {}

        historial = historial.dropna(subset=["Close"])

        # ----------------------------------------------------------
        # Precio inicial y final
        # ----------------------------------------------------------

        precio_inicial = historial["Close"].iloc[0]
        precio_final = historial["Close"].iloc[-1]

        fecha_inicial = historial.index[0]
        fecha_final = historial.index[-1]

        años = (fecha_final - fecha_inicial).days / 365.25

        # ----------------------------------------------------------
        # Retorno por precio
        # ----------------------------------------------------------

        cagr_precio = CAGR(
            precio_inicial,
            precio_final,
            años
        )

        crecimiento_precio = crecimiento_porcentual(
            precio_inicial,
            precio_final
        )

        # ==========================================================
        # DIVIDENDOS
        # ==========================================================

        if "Dividends" in historial.columns:

            dividendos = historial["Dividends"].fillna(0)

            total_dividendos = dividendos.sum()

        else:

            dividendos = pd.Series(
                0,
                index=historial.index
            )

            total_dividendos = 0

        # ----------------------------------------------------------
        # Dividendos anuales
        # ----------------------------------------------------------

        dividendos_anuales = dividendos.resample("YE").sum()

        dividendos_anuales = dividendos_anuales[
            dividendos_anuales > 0
        ]

        # ----------------------------------------------------------
        # CAGR de dividendos
        # ----------------------------------------------------------

        if len(dividendos_anuales) >= 2:

            dividendo_inicial = dividendos_anuales.iloc[0]
            dividendo_final = dividendos_anuales.iloc[-1]

            años_dividendos = (
                dividendos_anuales.index[-1]
                - dividendos_anuales.index[0]
            ).days / 365.25

            cagr_dividendos = CAGR(
                dividendo_inicial,
                dividendo_final,
                años_dividendos
            )

        else:

            dividendo_inicial = np.nan
            dividendo_final = np.nan
            cagr_dividendos = np.nan

        # ==========================================================
        # DIVIDEND YIELD HISTÓRICO
        # ==========================================================

        yields = []

        for fecha, dividendo in dividendos_anuales.items():

            año = fecha.year

            precios_año = historial[
                historial.index.year == año
            ]

            if precios_año.empty:
                continue

            precio_fin_año = precios_año["Close"].iloc[-1]

            if precio_fin_año > 0:

                yield_año = dividendo / precio_fin_año

                yields.append(yield_año)

        if yields:

            yield_promedio = np.mean(yields)
            yield_mediano = np.median(yields)
            yield_inicial = yields[0]
            yield_final = yields[-1]

        else:

            yield_promedio = np.nan
            yield_mediano = np.nan
            yield_inicial = np.nan
            yield_final = np.nan

        # ==========================================================
        # RETORNO TOTAL INCLUYENDO DIVIDENDOS
        # ==========================================================
        #
        # Usamos Adj Close porque incorpora dividendos y splits.
        #

        if "Adj Close" in historial.columns:

            adj_inicial = historial["Adj Close"].iloc[0]
            adj_final = historial["Adj Close"].iloc[-1]

            cagr_total_return = CAGR(
                adj_inicial,
                adj_final,
                años
            )

            retorno_total = crecimiento_porcentual(
                adj_inicial,
                adj_final
            )

        else:

            cagr_total_return = np.nan
            retorno_total = np.nan

        # ==========================================================
        # CRECIMIENTO DEL EPS
        # ==========================================================

        try:

            income_stmt = ticker.income_stmt

            eps_cagr = np.nan
            eps_inicial = np.nan
            eps_final = np.nan

            if income_stmt is not None and not income_stmt.empty:

                # Intentamos primero Diluted EPS
                posibles_eps = [
                    "Diluted EPS",
                    "Basic EPS"
                ]

                fila_eps = None

                for nombre in posibles_eps:

                    if nombre in income_stmt.index:
                        fila_eps = nombre
                        break

                if fila_eps is not None:

                    eps = income_stmt.loc[fila_eps].dropna()

                    eps = eps.sort_index()

                    eps = eps[
                        eps > 0
                    ]

                    if len(eps) >= 2:

                        eps_inicial = eps.iloc[0]
                        eps_final = eps.iloc[-1]

                        años_eps = (
                            eps.index[-1]
                            - eps.index[0]
                        ).days / 365.25

                        eps_cagr = CAGR(
                            eps_inicial,
                            eps_final,
                            años_eps
                        )

        except Exception:

            eps_cagr = np.nan
            eps_inicial = np.nan
            eps_final = np.nan

        # ==========================================================
        # CRECIMIENTO DE INGRESOS
        # ==========================================================

        try:

            revenue_cagr = np.nan

            if income_stmt is not None and not income_stmt.empty:

                if "Total Revenue" in income_stmt.index:

                    revenue = income_stmt.loc[
                        "Total Revenue"
                    ].dropna()

                    revenue = revenue.sort_index()

                    revenue = revenue[
                        revenue > 0
                    ]

                    if len(revenue) >= 2:

                        revenue_inicial = revenue.iloc[0]
                        revenue_final = revenue.iloc[-1]

                        años_revenue = (
                            revenue.index[-1]
                            - revenue.index[0]
                        ).days / 365.25

                        revenue_cagr = CAGR(
                            revenue_inicial,
                            revenue_final,
                            años_revenue
                        )

        except Exception:

            revenue_cagr = np.nan

        # ==========================================================
        # PAYOUT RATIO HISTÓRICO
        # ==========================================================

        payouts = []

        try:

            if income_stmt is not None and not income_stmt.empty:

                if "Diluted EPS" in income_stmt.index:

                    eps_hist = income_stmt.loc[
                        "Diluted EPS"
                    ].dropna()

                    eps_hist = eps_hist.sort_index()

                    for fecha, eps in eps_hist.items():

                        if eps <= 0:
                            continue

                        año = fecha.year

                        if año in dividendos_anuales.index.year:

                            dividendo = dividendos_anuales[
                                dividendos_anuales.index.year == año
                            ]

                            if not dividendo.empty:

                                dps = dividendo.iloc[0]

                                payout = dps / eps

                                if payout >= 0:

                                    payouts.append(payout)

        except Exception:

            pass

        if payouts:

            payout_promedio = np.mean(payouts)
            payout_mediano = np.median(payouts)
            payout_inicial = payouts[0]
            payout_final = payouts[-1]

        else:

            payout_promedio = np.nan
            payout_mediano = np.nan
            payout_inicial = np.nan
            payout_final = np.nan

        # ==========================================================
        # CRECIMIENTO DEL DIVIDENDO POR ACCIÓN
        # ==========================================================

        crecimiento_dividendo_total = (
            crecimiento_porcentual(
                dividendo_inicial,
                dividendo_final
            )
        )

        # ==========================================================
        # RESULTADO
        # ==========================================================

        return {

            "fecha_inicial_historial": fecha_inicial.date(),
            "fecha_final_historial": fecha_final.date(),

            "años_historial": años,

            "precio_inicial_hist": precio_inicial,
            "precio_final_hist": precio_final,

            "crecimiento_precio": crecimiento_precio,
            "cagr_precio": cagr_precio,

            "dividendos_totales_por_accion": total_dividendos,

            "dividendo_anual_inicial": dividendo_inicial,
            "dividendo_anual_final": dividendo_final,

            "crecimiento_dividendo_total": crecimiento_dividendo_total,
            "cagr_dividendos": cagr_dividendos,

            "yield_promedio": yield_promedio,
            "yield_mediano": yield_mediano,
            "yield_inicial": yield_inicial,
            "yield_final": yield_final,

            "retorno_total": retorno_total,
            "cagr_total_return": cagr_total_return,

            "eps_cagr": eps_cagr,
            "revenue_cagr": revenue_cagr,

            "payout_promedio": payout_promedio,
            "payout_mediano": payout_mediano,
            "payout_inicial": payout_inicial,
            "payout_final": payout_final,

        }

    except Exception as e:

        print(f"  ERROR en {symbol}: {e}")

        return {}


def main():

    # ==============================================================
    # LEER EXCEL
    # ==============================================================

    df = pd.read_excel(ARCHIVO_ENTRADA)

    resultados = []

    # ==============================================================
    # PROCESAR TICKERS
    # ==============================================================

    for symbol in df["ticker"].dropna().unique():

        datos = obtener_datos(symbol)

        datos["ticker"] = symbol

        resultados.append(datos)

    # ==============================================================
    # CREAR DATAFRAME DE RESULTADOS
    # ==============================================================

    df_nuevo = pd.DataFrame(resultados)

    # ==============================================================
    # UNIR CON EL EXCEL ORIGINAL
    # ==============================================================

    df_final = df.merge(
        df_nuevo,
        on="ticker",
        how="left"
    )

    # ==============================================================
    # GUARDAR
    # ==============================================================

    df_final.to_excel(
        ARCHIVO_SALIDA,
        index=False
    )

    print()
    print("=" * 60)
    print("PROCESO TERMINADO")
    print("=" * 60)
    print(f"Archivo generado: {ARCHIVO_SALIDA}")
    print(f"Acciones procesadas: {len(df_final)}")


if __name__ == "__main__":
    main()