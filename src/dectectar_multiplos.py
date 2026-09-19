import yfinance as yf
import pandas as pd

def obtener_bagger(symbol):
    try:
        ticker = yf.Ticker(symbol)
        try:
            info = ticker.info
            sector = info.get('sector', None)
            industria = info.get('industry', None)
        except:
            sector = None
            industria = None
        historial = ticker.history(
            period="max",
            interval="1d",
            auto_adjust=True,
            actions=False
        )
    except:
        return None
    historial = historial[
        ["Close", "High"]
    ].copy()
    historial = historial.dropna(
        subset=["Close", "High"]
    )
    historial = historial[
        (historial["Close"] > 0) &
        (historial["High"] > 0)
    ]
    historial = historial.sort_index()
    precio_inicial = float(
        historial["Close"].iloc[0]
    )
    fecha_inicial = historial.index[0]
    indice_maximo = historial["High"].idxmax()
    precio_maximo = float(
        historial.loc[indice_maximo, "High"]
    )
    fecha_maximo = indice_maximo
    multiplicador = precio_maximo / precio_inicial
    dias_total = (
        fecha_maximo - fecha_inicial
    ).days
    years_total = dias_total / 365.25
    objetivo_50 = precio_inicial * 50
    dias_hasta_50 = None
    years_hasta_50 = None
    alcanzado_50 = historial[
        historial["High"] >= objetivo_50
    ]
    if not alcanzado_50.empty:
        fecha_50 = alcanzado_50.index[0]
        dias_hasta_50 = (
            fecha_50 - fecha_inicial
        ).days
        years_hasta_50 = dias_hasta_50 / 365.25
    return (
        sector,
        industria,
        precio_inicial,
        precio_maximo,
        multiplicador,
        years_hasta_50,
        years_total
    )

df = pd.read_excel('universo_total.xlsx')

for i in range(len(df)):
    salida = obtener_bagger(df.loc[i, 'ticker'])
    df.loc[i, 'sector'] = salida[0]
    df.loc[i, 'industria'] = salida[1]
    df.loc[i, 'precio_inicial'] = salida[2]
    df.loc[i, 'precio_maximo'] = salida[3]
    df.loc[i, 'multiplicador'] = salida[4]
    df.loc[i, 'years_hasta_50'] = salida[5]
    df.loc[i, 'years_total'] = salida[6]

df = df[df['multiplicador'] >= 50]
df = df[df['years_hasta_50'] >= 1]
df = df[df['years_total'] >= 1]
df['cagr_50'] = (50 ** (1 / df['years_hasta_50'])) - 1
df['cagr'] = (df['multiplicador'] ** (1 / df['years_total'])) - 1

df.to_excel('universo_definitivo.xlsx', index=False)
