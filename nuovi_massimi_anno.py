import os
import dash
from dash import html, dcc
import dash.dependencies as dd
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval
from ricerca import get_search_layout, register_search_callbacks

# Inizializzazione dell'app Dash (Worker)
app = dash.Dash(__name__, server=False)

# Connessione a TradingView
tv = TvDatafeed()

# Layout della pagina per i nuovi massimi annuali
layout = html.Div(style={'backgroundColor': '#121212', 'color': 'white', 'padding': '20px'}, children=[
    html.H1("Nuovi Massimi nell'Anno", style={'textAlign': 'center', 'color': 'cyan'}),

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
                dcc.Graph(id='grafico-nuovi-massimi'),
                dcc.Graph(id='grafico-contatore-massimi'),
                dcc.Graph(id='grafico-rendimento-annuo'),
                dcc.Graph(id='grafico-scatter')
            ])
        ]
    )
])

app.layout = layout

# ✅ Registra i callback della ricerca direttamente nel worker
register_search_callbacks(app)

# Funzione per ottenere i dati dei nuovi massimi annuali
def get_asset_data(ticker):
    try:
        if not ticker:
            return None

        exchange, symbol = ticker.split(":") if ":" in ticker else ("", ticker)
        asset_data = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=10000)

        if asset_data is None or asset_data.empty:
            return None

        asset_data.index = pd.to_datetime(asset_data.index).tz_localize(None)
        asset_data.sort_index(inplace=True)
        asset_data.rename(columns={'close': 'Close'}, inplace=True)

        # Calcolo nuovi massimi annuali
        asset_data['year'] = asset_data.index.year
        asset_data['rolling_max_year'] = asset_data.groupby('year')['Close'].cummax()
        asset_data['rolling_max_shifted_year'] = asset_data.groupby('year')['rolling_max_year'].shift(1)
        asset_data['is_new_high_year'] = asset_data['Close'] > asset_data['rolling_max_shifted_year']
        asset_data['new_high_count_year'] = asset_data.groupby('year')['is_new_high_year'].cumsum()

        # Analisi aggregata per anno
        yearly_data = asset_data.groupby('year').agg(
            number_of_new_highs=('is_new_high_year', 'sum'),
            first_close=('Close', 'first'),
            last_close=('Close', 'last')
        )
        yearly_data['yearly_return_pct'] = 100.0 * (yearly_data['last_close'] / yearly_data['first_close'] - 1)
        yearly_data.reset_index(inplace=True)

        return asset_data, yearly_data

    except Exception as e:
        print(f"Errore nel recupero dati: {str(e)}")
        return None

# ✅ Callback per aggiornare i grafici dopo la selezione del ticker
def update_graphs(ticker):
    if not ticker:
        return go.Figure(), go.Figure(), go.Figure(), go.Figure()

    data = get_asset_data(ticker)

    if data is None:
        return go.Figure(), go.Figure(), go.Figure(), go.Figure()

    df, yearly_data = data

    # 🔹 Grafico massimi annuali
    nuovi_massimi_fig = go.Figure()
    nuovi_massimi_fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'], mode='lines', name='Prezzo', line=dict(color='blue')))
    nuovi_massimi_fig.add_trace(go.Scatter(
        x=df.index[df['is_new_high_year']],
        y=df.loc[df['is_new_high_year'], 'Close'],
        mode='markers', marker=dict(color='red', size=5), name='Nuovi Massimi Anno'))
    nuovi_massimi_fig.update_layout(title=f"{ticker} Nuovi Massimi Annuali",
                                    xaxis_title="Anno", yaxis_title="Prezzo",
                                    height=500, paper_bgcolor='#121212',
                                    plot_bgcolor='#121212', font=dict(color='white'))

    # 🔹 Grafico contatore nuovi massimi
    contatore_massimi_fig = go.Figure()
    contatore_massimi_fig.add_trace(go.Scatter(
        x=df.index, y=df['new_high_count_year'], mode='lines', name="Conteggio Nuovi Massimi", line=dict(color='orange')))
    contatore_massimi_fig.update_layout(title="Conteggio Nuovi Massimi per Anno",
                                        xaxis_title="Anno", yaxis_title="Conteggio",
                                        height=500, paper_bgcolor='#121212',
                                        plot_bgcolor='#121212', font=dict(color='white'))

    # 🔹 Grafico rendimento annuo
    rendimento_annuo_fig = go.Figure(data=[
        go.Bar(x=yearly_data['year'], y=yearly_data['yearly_return_pct'], name="Rendimento Annuo", marker_color='green')
    ])
    rendimento_annuo_fig.update_layout(title=f"{ticker} Rendimento Annuo (%)",
                                       xaxis_title="Anno", yaxis_title="Rendimento (%)",
                                       height=500, paper_bgcolor='#121212',
                                       plot_bgcolor='#121212', font=dict(color='white'))

    # 🔹 Scatter nuovi massimi vs rendimento annuo
    scatter_fig = go.Figure()
    colors = ['red' if r < 0 else 'green' for r in yearly_data['yearly_return_pct']]
    scatter_fig.add_trace(go.Scatter(
        x=yearly_data['number_of_new_highs'],
        y=yearly_data['yearly_return_pct'],
        mode='markers',
        marker=dict(color=colors, size=8),
        name="Dati Storici"
    ))
    scatter_fig.add_hline(y=0, line_dash="dash", line_color="black")
    scatter_fig.update_layout(title=f"{ticker}: Nuovi Massimi vs Rendimento Annuo",
                              xaxis_title="Numero di Nuovi Massimi",
                              yaxis_title="Rendimento (%)",
                              height=500, paper_bgcolor='#121212',
                              plot_bgcolor='#121212', font=dict(color='white'))

    return nuovi_massimi_fig, contatore_massimi_fig, rendimento_annuo_fig, scatter_fig

# ✅ Funzione per registrare i callback nel server principale
def register_callbacks(app):
    """ Registra i callback dell'analisi dei nuovi massimi nell'app principale """
    app.callback(
        [dd.Output('grafico-nuovi-massimi', 'figure'),
         dd.Output('grafico-contatore-massimi', 'figure'),
         dd.Output('grafico-rendimento-annuo', 'figure'),
         dd.Output('grafico-scatter', 'figure')],
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
