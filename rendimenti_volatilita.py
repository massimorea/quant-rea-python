import os
import dash
from dash import html, dcc  # Modificato qui
import dash.dependencies as dd
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval
from ricerca import get_search_layout, register_search_callbacks

# Inizializzazione dell'app Dash
app = dash.Dash(__name__, server=False)

# Connessione a TradingView
tv = TvDatafeed()

# Layout dell'app, ora usa la ricerca con selezione automatica
layout = html.Div(style={'backgroundColor': '#121212', 'color': 'white', 'padding': '20px'}, children=[
    html.H1("QUANT-REA: Analisi Volatilità Asset", style={'textAlign': 'center', 'color': 'cyan'}),

    # Sezione di ricerca con valore selezionato
    get_search_layout(),

    # Messaggio di caricamento AJAX
    html.Div(id='loading-message', style={'color': 'yellow', 'marginTop': '10px', 'textAlign': 'center', 'display': 'none'}),

    # Spinner di caricamento
    dcc.Loading(
        id="loading-spinner",
        type="circle",
        children=[
            html.Div(id='output-container', children=[
                dcc.Graph(id='grafico-rendimento-giornaliero'),
                dcc.Graph(id='grafico-rendimento-settimanale'),
                dcc.Graph(id='grafico-rendimento-mensile'),
                dcc.Graph(id='grafico-volatilita')
            ])
        ]
    ),

    # JavaScript per gestire il caricamento AJAX
    html.Script('''
        document.addEventListener("DOMContentLoaded", function() {
            let tickerInput = document.getElementById("selected-ticker");
            let loadingMessage = document.getElementById("loading-message");
            
            tickerInput.addEventListener("change", function() {
                loadingMessage.style.display = "block";
                loadingMessage.innerText = "🔄 Caricamento dati in corso...";
                
                setTimeout(() => {
                    loadingMessage.style.display = "none";
                }, 5000);
            });
        });
    ''')
])

app.layout = layout

# Funzione per ottenere i dati SOLO da TradingView
def get_asset_data(ticker):
    try:
        if not ticker:
            return None

        exchange, symbol = ticker.split(":") if ":" in ticker else ("", ticker)
        asset_data = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=100000)

        if asset_data is None or asset_data.empty:
            return None

        asset_data['Rendimento_Giornaliero'] = asset_data['close'].pct_change()
        asset_data['Rendimento_Settimanale'] = asset_data['Rendimento_Giornaliero'].rolling(5).sum()
        asset_data['Rendimento_Mensile'] = asset_data['Rendimento_Giornaliero'].rolling(22).sum()
        asset_data['Volatilità_Giornaliera'] = asset_data['Rendimento_Giornaliero'].rolling(window=30).std() * np.sqrt(365)

        return asset_data
    except Exception as e:
        print(f"Errore nel recupero dati: {str(e)}")  # Aggiunto log dell'errore
        return None

# Callback per aggiornare automaticamente i grafici dopo la selezione del ticker
def update_graphs(ticker):
    if not ticker:
        return go.Figure(), go.Figure(), go.Figure(), go.Figure()

    data = get_asset_data(ticker)

    if data is None:
        return go.Figure(), go.Figure(), go.Figure(), go.Figure()

    rendimento_giornaliero_fig = go.Figure(data=[
        go.Bar(x=data.index, y=data['Rendimento_Giornaliero'] * 100, name="Rendimento Giornaliero", marker_color='blue')
    ])
    rendimento_giornaliero_fig.update_layout(title=f"Rendimento Giornaliero - {ticker}", xaxis_title="Anno",
                                             yaxis_title="Rendimento (%)", height=500, paper_bgcolor='#121212',
                                             plot_bgcolor='#121212', font=dict(color='white'))

    rendimento_settimanale_fig = go.Figure(data=[
        go.Bar(x=data.index, y=data['Rendimento_Settimanale'] * 100, name="Rendimento Settimanale", marker_color='green')
    ])
    rendimento_settimanale_fig.update_layout(title=f"Rendimento Settimanale - {ticker}", xaxis_title="Anno",
                                             yaxis_title="Rendimento (%)", height=500, paper_bgcolor='#121212',
                                             plot_bgcolor='#121212', font=dict(color='white'))

    rendimento_mensile_fig = go.Figure(data=[
        go.Bar(x=data.index, y=data['Rendimento_Mensile'] * 100, name="Rendimento Mensile", marker_color='orange')
    ])
    rendimento_mensile_fig.update_layout(title=f"Rendimento Mensile - {ticker}", xaxis_title="Anno",
                                         yaxis_title="Rendimento (%)", height=500, paper_bgcolor='#121212',
                                         plot_bgcolor='#121212', font=dict(color='white'))

    volatilita_fig = go.Figure(data=[
        go.Scatter(x=data.index, y=data['Volatilità_Giornaliera'], mode='lines', name="Volatilità Annualizzata",
                   line=dict(color='red'))
    ])
    volatilita_fig.update_layout(title=f"Volatilità - {ticker}", xaxis_title="Data", yaxis_title="Volatilità",
                                 height=500, paper_bgcolor='#121212', plot_bgcolor='#121212', font=dict(color='white'))

    return rendimento_giornaliero_fig, rendimento_settimanale_fig, rendimento_mensile_fig, volatilita_fig

# ✅ Funzione per registrare i callback nell'app principale (usata in app.py)
def register_callbacks(app):
    """ Registra i callback dell'analisi della volatilità nell'app principale """
    app.callback(
        [dd.Output('grafico-rendimento-giornaliero', 'figure'),
         dd.Output('grafico-rendimento-settimanale', 'figure'),
         dd.Output('grafico-rendimento-mensile', 'figure'),
         dd.Output('grafico-volatilita', 'figure')],
        [dd.Input('selected-ticker', 'value')]
    )(update_graphs)  # Usa la funzione di aggiornamento dei grafici

# Registra le funzioni di ricerca
register_search_callbacks(app)

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
