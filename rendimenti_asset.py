import os
import dash
from dash import html, dcc
import dash.dependencies as dd
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy.stats import zscore
from tvDatafeed import TvDatafeed, Interval
from ricerca import get_search_layout, register_search_callbacks

# Inizializzazione dell'app Dash (Worker)
app = dash.Dash(__name__, server=False)

# Connessione a TradingView
tv = TvDatafeed()

# Layout della pagina per i rendimenti degli asset
layout = html.Div(style={'backgroundColor': '#121212', 'color': 'white', 'padding': '20px'}, children=[
    html.H1("Analisi Rendimenti Asset", style={'textAlign': 'center', 'color': 'cyan'}),

    # ✅ Sezione di ricerca con valore selezionato
    get_search_layout(),

    # ✅ Input nascosto per salvare il ticker selezionato
    dcc.Input(id='selected-ticker', type='text', value="", style={'display': 'none'}),

    # Messaggio di caricamento AJAX
    html.Div(id='loading-message', style={'color': 'yellow', 'marginTop': '10px', 'textAlign': 'center', 'display': 'none'}),

    # Spinner di caricamento
    dcc.Loading(
        id="loading-spinner",
        type="circle",
        children=[
            html.Div(id='output-container', children=[
                dcc.Graph(id='grafico-rendimento-annuale'),
                dcc.Graph(id='grafico-zscore')
            ])
        ]
    )
])

app.layout = layout

# ✅ Registra i callback della ricerca direttamente nel worker
register_search_callbacks(app)

# Funzione per ottenere i dati dello S&P 500 da TradingView
def get_asset_data(ticker):
    try:
        if not ticker:
            return None

        exchange, symbol = ticker.split(":") if ":" in ticker else ("", ticker)
        asset_data = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=50000)

        if asset_data is None or asset_data.empty:
            return None

        asset_data.index = pd.to_datetime(asset_data.index)
        asset_data = asset_data.sort_index()

        # Rendimenti annuali
        asset_data['Year'] = asset_data.index.year
        annual_data = asset_data.groupby('Year')['close'].last().pct_change().dropna()
        annual_data = annual_data.squeeze()

        annualized_return = annual_data.mean()
        annualized_std = annual_data.std()
        annual_data_zscore = zscore(annual_data)

        results = pd.DataFrame({
            'Year': annual_data.index,
            'Annual Return': annual_data.values,
            'Z-Score': annual_data_zscore
        })

        return results, annualized_return, annualized_std

    except Exception as e:
        print(f"Errore nel recupero dati: {str(e)}")
        return None

# ✅ Callback per aggiornare i grafici dopo la selezione del ticker
def update_graphs(ticker):
    if not ticker:
        return go.Figure(), go.Figure()

    data = get_asset_data(ticker)

    if data is None:
        return go.Figure(), go.Figure()

    results, annualized_return, annualized_std = data

    rendimento_annuale_fig = go.Figure(data=[
        go.Bar(x=results['Year'], y=results['Annual Return'] * 100, name="Rendimento Annuale", marker_color='blue')
    ])
    rendimento_annuale_fig.add_hline(y=annualized_return * 100, line_dash="dash", line_color="red",
                                     annotation_text="Media", annotation_position="top right")
    rendimento_annuale_fig.add_hline(y=(annualized_return + annualized_std) * 100, line_dash="dash", line_color="green")
    rendimento_annuale_fig.add_hline(y=(annualized_return - annualized_std) * 100, line_dash="dash", line_color="green")

    rendimento_annuale_fig.update_layout(title=f"Rendimento Annuale - {ticker}", xaxis_title="Anno",
                                         yaxis_title="Rendimento (%)", height=500, paper_bgcolor='#121212',
                                         plot_bgcolor='#121212', font=dict(color='white'))

    zscore_fig = go.Figure(data=[
        go.Scatter(x=results['Year'], y=results['Z-Score'], mode='lines+markers', name="Z-Score", line=dict(color='orange'))
    ])
    zscore_fig.add_hline(y=0, line_dash="dash", line_color="white")
    zscore_fig.add_hline(y=1, line_dash="dash", line_color="gray")
    zscore_fig.add_hline(y=-1, line_dash="dash", line_color="gray")

    zscore_fig.update_layout(title=f"Z-Score dei Rendimenti - {ticker}", xaxis_title="Anno",
                             yaxis_title="Z-Score", height=500, paper_bgcolor='#121212',
                             plot_bgcolor='#121212', font=dict(color='white'))

    return rendimento_annuale_fig, zscore_fig

# ✅ Funzione per registrare i callback nel server principale
def register_callbacks(app):
    """ Registra i callback dell'analisi dei rendimenti nell'app principale """
    app.callback(
        [dd.Output('grafico-rendimento-annuale', 'figure'),
         dd.Output('grafico-zscore', 'figure')],
        [dd.Input('selected-ticker', 'value')]
    )(update_graphs)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', action='store_true', help='Run as worker')
    args = parser.parse_args()

    if args.worker:
        # Modalità worker: mantiene il processo in esecuzione
        import time
        while True:
            time.sleep(1)
    else:
        # Modalità normale: avvia il server
        port = int(os.environ.get("PORT", 5000))
        app.run_server(host='0.0.0.0', port=port)
