# Análisis de 50-Baggers Chilenas 🇨🇱📈

Un estudio inspirado en *100 Baggers: Stocks That Return 100-to-1 and How to Find Them*, de **Christopher Mayer**, aplicado a la Bolsa de Santiago. En lugar de buscar acciones que multiplicaron su precio por 100 —el estándar de Mayer para el mercado estadounidense—, este proyecto rastrea acciones chilenas que en algún momento de su historia multiplicaron por **al menos 50 veces** su primer precio disponible: las **50-baggers**.

El repositorio contiene el código de recolección de datos, los datos crudos y procesados, y el paper de investigación resultante.

## ¿Qué es una "50-bagger"?

El término *bagger* proviene de la jerga beisbolera que usa Peter Lynch (y luego Mayer) para describir una acción que multiplica el capital invertido: un *10-bagger* devuelve 10 veces lo invertido, un *100-bagger* devuelve 100 veces. Aquí adaptamos el umbral a 50x porque la Bolsa de Santiago es un mercado mucho más chico, concentrado y con menos historia de datos abiertos que el mercado estadounidense que estudió Mayer, por lo que exigir un múltiplo de 100x hubiera dejado el universo casi vacío.

Concretamente, una acción se clasifica como 50-bagger si:

- El precio **máximo histórico** (ajustado por splits y dividendos) fue al menos **50 veces** el primer precio de cierre disponible en el historial.
- Ese múltiplo se alcanzó en **al menos 1 año** desde el inicio del historial (para excluir artefactos de IPO/primeros días de cotización).
- El historial total disponible es de **al menos 1 año**.

## Resultado

Sobre un universo inicial de **92 tickers** de la Bolsa de Santiago (sufijo `.SN` en Yahoo Finance), **12 acciones** cumplen el criterio de 50-bagger:

| Ticker | Empresa (referencia) | Sector | Múltiplo máx. | Años hasta 50x | CAGR hasta 50x |
|---|---|---|---:|---:|---:|
| BSANTANDER.SN | Banco Santander‑Chile | Financiero | 187x | 5.5 | 104.0% |
| QUINENCO.SN | Quiñenco S.A. | Energía / Holding | 95x | 6.5 | 82.8% |
| PLANVITAL.SN | AFP PlanVital | Financiero | 119x | 11.4 | 40.9% |
| PUCOBRE.SN | Sociedad Punta del Cobre | Materiales básicos | 126x | 25.9 | 16.3% |
| SQM-B.SN | SQM (Serie B) | Materiales básicos | 113x | 21.8 | 19.6% |
| NAVIERA.SN | Grupo Empresas Navieras (AGUNSA) | Industrial | 91x | 23.1 | 18.4% |
| SQM-A.SN | SQM (Serie A) | Materiales básicos | 73x | 22.2 | 19.3% |
| PROVIDA.SN | AFP Provida | Financiero | 77x | 25.2 | 16.8% |
| HABITAT.SN | AFP Habitat | Financiero | 63x | 25.7 | 16.4% |
| BICE.SN | BICECORP | Financiero | 85x | 25.0 | 16.9% |
| BANVIDA.SN | Banvida S.A. | Financiero | 54x | 26.0 | 16.2% |
| ECL.SN | Engie Energía Chile | Utilities | 52x | 26.3 | 16.0% |

> Nota: el múltiplo se mide contra el **máximo histórico** de cada acción, no contra su precio actual. Varias de estas acciones (SQM, Quiñenco, BSANTANDER) cotizan hoy muy por debajo de ese máximo. El análisis completo, con todas las salvedades metodológicas, está en el paper (ver abajo).

## Estructura del repositorio

```
.
├── data/
│   ├── universo_total.xlsx                # Universo de partida: 92 tickers .SN
│   ├── universo_definitivo.xlsx           # Los 12 tickers que superan el filtro de 50x
│   └── universo_definitivo_completo.xlsx  # universo_definitivo.xlsx + datos fundamentales
├── src/
│   ├── dectectar_multiplos.py             # Filtra el universo por múltiplo ≥ 50x
│   └── info_clave.py                      # Enriquece con dividendos, EPS, ingresos, payout
├── LICENSE
└── README.md
```

## Metodología (resumen)

1. **`dectectar_multiplos.py`** descarga, vía [`yfinance`](https://github.com/ranaroussi/yfinance), el historial de precios máximo disponible (ajustado por splits/dividendos) para cada ticker en `universo_total.xlsx`, calcula el múltiplo `precio_máximo / precio_inicial` y filtra los que superan 50x.
2. **`info_clave.py`** toma ese subconjunto y agrega, para cada ticker: crecimiento y CAGR del precio (sin ajustar), dividendos totales y su CAGR, *dividend yield* histórico, retorno total (con `Adj Close`), CAGR de EPS e ingresos (a partir del estado de resultados anual expuesto por `yfinance`, normalmente 4 años), y ratios de *payout*.
3. Los archivos de salida quedan en `data/`.

Para reproducir el pipeline:

```bash
pip install yfinance pandas openpyxl numpy
python src/dectectar_multiplos.py   # genera universo_definitivo.xlsx
python src/info_clave.py            # genera universo_definitivo_completo.xlsx
```

## Limitaciones importantes (léelas antes de citar los números)

- **El historial de precios no siempre coincide con la fecha real de IPO.** Para varios tickers, Yahoo Finance solo entrega datos desde el 2000‑01‑03 en adelante, aunque la empresa cotice en bolsa desde mucho antes (Quiñenco, por ejemplo, es una matriz de inversiones que opera desde 1957). Los "años hasta 50x" deben leerse como "años desde que hay datos", no como la vida bursátil real de la acción.
- **Precios ajustados vs. sin ajustar.** El múltiplo de 50x usa precios ajustados por splits y dividendos; otras columnas del archivo enriquecido (como `precio_inicial_hist` / `precio_final_hist`) usan precios sin ajustar. Mezclar ambas series sin cuidado puede generar lecturas confusas, especialmente en tickers con eventos corporativos grandes (ej. BSANTANDER).
- **Sesgo de supervivencia.** Solo se analizan empresas que siguen cotizando hoy. Empresas que fueron 50-baggers y luego quebraron, se deslistaron o fueron absorbidas por otra compañía (vía OPA o fusión) no aparecen en `universo_total.xlsx` y por lo tanto no pueden ser detectadas por este pipeline.
- **CAGR de EPS/ingresos de corto plazo.** `yfinance` solo expone unos 4 años de estado de resultados anual, por lo que `eps_cagr` y `revenue_cagr` reflejan una ventana reciente y **no** el crecimiento de utilidades a lo largo de las dos o tres décadas que tomó alcanzar el múltiplo de 50x.
- **Columnas de *payout* poco confiables.** Algunos valores de `payout_promedio`/`payout_mediano` superan el 100% (incluso 300%–700%) por inconsistencias de unidades/denominadores casi nulos en el EPS reportado por el proveedor de datos. Se muestran igual por transparencia, pero deben tratarse con escepticismo.
- **Cifras nominales en pesos chilenos**, sin ajuste por inflación ni por depreciación del CLP frente al dólar.
- **Muestra pequeña (n = 12).** Esto es un estudio descriptivo/cualitativo, en el espíritu del libro de Mayer, no un estudio estadístico con significancia formal.

## El paper

El análisis completo —incluyendo el contexto de cada una de las 12 empresas antes de convertirse en 50-baggers (qué tipo de negocio eran, si ya eran rentables, quién las controlaba, y qué las hizo despegar), el paralelo con el marco de Christopher Mayer, y las lecciones para inversores chilenos— está publicado como paper de investigación:

- **PDF en este repositorio:** [`paper/50_baggers_chilenas.pdf`](./paper/50_baggers_chilenas.pdf)
- **SSRN:** _(enlace a publicar)_

## Autor

**Iñaki Salcedo** — [github.com/inakisalcedo](https://github.com/inakisalcedo)

## Licencia

Este proyecto está licenciado bajo la licencia MIT — ver [`LICENSE`](./LICENSE).

## Descargo de responsabilidad

Este repositorio y el paper asociado tienen **fines exclusivamente educativos y de investigación**. Nada aquí constituye una recomendación de inversión. Los rendimientos pasados —y menos aún un máximo histórico puntual— no garantizan resultados futuros. Antes de tomar decisiones de inversión, consulta a un asesor financiero registrado.
