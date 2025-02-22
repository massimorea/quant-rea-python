import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval

# Inizializzazione dell'app Dash
app = dash.Dash(__name__)
server = app.server  # Necessario per Heroku

# Connessione a TradingView
tv = TvDatafeed()

# Layout dell'app con tasto e segnale di download
app.layout = html.Div(style={'backgroundColor': '#121212', 'color': 'white', 'padding': '20px'}, children=[
    html.H1("QUANT-REA: Analisi Volatilità Asset", style={'textAlign': 'center', 'color': 'cyan'}),

    html.Div([
        html.Label("Inserisci un ticker TradingView (es. BINANCE:BTCUSDT, NASDAQ:AAPL):", style={'color': 'white'}),
        dcc.Input(id='ticker-input', type='text', value='BINANCE:BTCUSDT', debounce=True, style={'marginLeft': '10px'}),
        html.Button("Analizza", id='analyze-button', n_clicks=0, style={'marginLeft': '10px', 'backgroundColor': 'cyan'}),
        html.Div(id='loading-message', style={'color': 'yellow', 'marginTop': '10px', 'fontSize': '16px', 'fontWeight': 'bold'}),
        html.Div(id='ticker-warning', style={'color': 'red', 'marginTop': '5px'})  
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),

    html.Div(id='output-container', children=[
        dcc.Graph(id='grafico-rendimento-giornaliero'),
        dcc.Graph(id='grafico-rendimento-settimanale'),
        dcc.Graph(id='grafico-rendimento-mensile'),
        dcc.Graph(id='grafico-volatilita')
    ])
])


# Funzione per ottenere i dati SOLO da TradingView
def get_asset_data(ticker):
    try:
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
        return None


# Callback per aggiornare i grafici solo dopo il click sul bottone
@app.callback(
    [dd.Output('grafico-rendimento-giornaliero', 'figure'),
     dd.Output('grafico-rendimento-settimanale', 'figure'),
     dd.Output('grafico-rendimento-mensile', 'figure'),
     dd.Output('grafico-volatilita', 'figure'),
     dd.Output('ticker-warning', 'children'),
     dd.Output('loading-message', 'children')],
    [dd.Input('analyze-button', 'n_clicks')],
    [dd.State('ticker-input', 'value')]
)
def update_graphs(n_clicks, ticker):
    if n_clicks == 0:
        return go.Figure(), go.Figure(), go.Figure(), go.Figure(), "", ""  # Nessun update iniziale

    # ✅ **Mostra il messaggio "Caricamento in corso..." mentre i dati vengono aggiornati**
    loading_message = "⏳ Caricamento in corso..."

    # **Mostra il messaggio mentre scarica i dati**
    yield dash.no_update, dash.no_update, dash.no_update, dash.no_update, "", loading_message

    # ✅ **Scarica i nuovi dati**
    data = get_asset_data(ticker)

    if data is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, "⚠️ Ticker non valido.", ""

    warning_message = ""

    rendimento_giornaliero_fig = go.Figure(data=[
        go.Bar(x=data.index, y=data['Rendimento_Giornaliero'] * 100, name="Rendimento Giornaliero", marker_color='blue')
    ])
    rendimento_giornaliero_fig.update_layout(title="Rendimento Giornaliero", xaxis_title="Anno",
                                             yaxis_title="Rendimento (%)", height=500, paper_bgcolor='#121212',
                                             plot_bgcolor='#121212', font=dict(color='white'))

    rendimento_settimanale_fig = go.Figure(data=[
        go.Bar(x=data.index, y=data['Rendimento_Settimanale'] * 100, name="Rendimento Settimanale", marker_color='green')
    ])
    rendimento_settimanale_fig.update_layout(title="Rendimento Settimanale", xaxis_title="Anno",
                                             yaxis_title="Rendimento (%)", height=500, paper_bgcolor='#121212',
                                             plot_bgcolor='#121212', font=dict(color='white'))

    rendimento_mensile_fig = go.Figure(data=[
        go.Bar(x=data.index, y=data['Rendimento_Mensile'] * 100, name="Rendimento Mensile", marker_color='orange')
    ])
    rendimento_mensile_fig.update_layout(title="Rendimento Mensile", xaxis_title="Anno",
                                         yaxis_title="Rendimento (%)", height=500, paper_bgcolor='#121212',
                                         plot_bgcolor='#121212', font=dict(color='white'))

    volatilita_fig = go.Figure(data=[
        go.Scatter(x=data.index, y=data['Volatilità_Giornaliera'], mode='lines', name="Volatilità Annualizzata",
                   line=dict(color='red'))
    ])
    volatilita_fig.update_layout(title="Volatilità", xaxis_title="Data", yaxis_title="Volatilità",
                                 height=500, paper_bgcolor='#121212', plot_bgcolor='#121212', font=dict(color='white'))

    # ✅ **Nasconde il messaggio di caricamento dopo aver aggiornato i grafici**
    return rendimento_giornaliero_fig, rendimento_settimanale_fig, rendimento_mensile_fig, volatilita_fig, warning_message, ""

# Avvia il server
if __name__ == '__main__':
    app.run_server(debug=True)
