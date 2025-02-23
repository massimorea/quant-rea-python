import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval

# Importa layout e callback di ricerca dal tuo file "ricerca.py"
from ricerca import get_search_layout, register_search_callbacks

app = dash.Dash(__name__)
server = app.server  # Per Heroku

# Connessione a TradingView
tv = TvDatafeed()

# Layout principale dell'app
# - Includiamo il layout di ricerca (autocomplete) definito in ricerca.py
# - Aggiungiamo il bottone "Analizza"
# - Aggiungiamo i grafici e i messaggi
app.layout = html.Div(style={'backgroundColor': '#121212', 'color': 'white', 'padding': '20px'}, children=[

    html.H1("QUANT-REA: Analisi Volatilità Asset", style={'textAlign': 'center', 'color': 'cyan'}),

    # Layout di ricerca (input+dropdown) importato da ricerca.py
    get_search_layout(),

    # Bottone per avviare l'analisi
    html.Button("Analizza", id='analyze-button', n_clicks=0,
                style={'marginLeft': '10px', 'backgroundColor': 'cyan'}),

    # Messaggi di avviso e caricamento
    html.Div(id='ticker-warning', style={'color': 'red', 'marginTop': '5px', 'textAlign': 'center'}),
    html.Div(id='loading-message', style={'color': 'yellow', 'marginTop': '10px',
                                          'fontSize': '16px', 'fontWeight': 'bold', 'textAlign': 'center'}),

    # Grafici
    dcc.Graph(id='grafico-rendimento-giornaliero'),
    dcc.Graph(id='grafico-rendimento-settimanale'),
    dcc.Graph(id='grafico-rendimento-mensile'),
    dcc.Graph(id='grafico-volatilita')
])

# Registra i callback di ricerca (autocomplete) dal modulo ricerca.py
register_search_callbacks(app)

def get_asset_data(ticker):
    """
    Scarica i dati dal ticker TradingView selezionato (es. NASDAQ:AAPL).
    Calcola rendimenti e volatilità, restituendo un DataFrame con le colonne:
    - Rendimento_Giornaliero
    - Rendimento_Settimanale
    - Rendimento_Mensile
    - Volatilità_Giornaliera
    """
    try:
        exchange, symbol = ticker.split(":") if ":" in ticker else ("", ticker)
        asset_data = tv.get_hist(symbol=symbol, exchange=exchange,
                                 interval=Interval.in_daily, n_bars=100000)
        if asset_data is None or asset_data.empty:
            return None

        asset_data['Rendimento_Giornaliero'] = asset_data['close'].pct_change()
        asset_data['Rendimento_Settimanale'] = asset_data['Rendimento_Giornaliero'].rolling(5).sum()
        asset_data['Rendimento_Mensile'] = asset_data['Rendimento_Giornaliero'].rolling(22).sum()
        asset_data['Volatilità_Giornaliera'] = (
            asset_data['Rendimento_Giornaliero']
            .rolling(window=30).std()
            * np.sqrt(365)
        )
        return asset_data
    except Exception as e:
        return None

# Callback per avviare l'analisi quando si preme il bottone "Analizza"
@app.callback(
    [
        dd.Output('grafico-rendimento-giornaliero', 'figure'),
        dd.Output('grafico-rendimento-settimanale', 'figure'),
        dd.Output('grafico-rendimento-mensile', 'figure'),
        dd.Output('grafico-volatilita', 'figure'),
        dd.Output('ticker-warning', 'children'),
        dd.Output('loading-message', 'children')
    ],
    [dd.Input('analyze-button', 'n_clicks')],
    [dd.State('search-dropdown', 'value')]
)
def update_graphs(n_clicks, selected_ticker):
    """
    1) Se n_clicks=0, non aggiorna nulla (prima apertura).
    2) Se non c'è un ticker selezionato nel dropdown, avvisa l'utente.
    3) Altrimenti scarica i dati e costruisce i grafici.
    """
    if n_clicks == 0:
        return (go.Figure(), go.Figure(), go.Figure(), go.Figure(), "", "")

    loading_message = "🔄 Scaricamento dati, attendere..."

    if not selected_ticker:
        return (go.Figure(), go.Figure(), go.Figure(), go.Figure(),
                "⚠️ Seleziona un ticker dalla lista!", "")

    data = get_asset_data(selected_ticker)
    if data is None:
        return (go.Figure(), go.Figure(), go.Figure(), go.Figure(),
                f"⚠️ Ticker '{selected_ticker}' non valido.", "")

    # Se arrivo qui, ho i dati
    warning_message = ""
    # Grafico Giornaliero
    fig_giornaliero = go.Figure(data=[
        go.Bar(x=data.index, y=data['Rendimento_Giornaliero']*100,
               name="Rendimento Giornaliero", marker_color='blue')
    ])
    fig_giornaliero.update_layout(
        title=f"Rendimento Giornaliero ({selected_ticker})",
        xaxis_title="Anno",
        yaxis_title="Rendimento (%)",
        height=500,
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        font=dict(color='white')
    )

    # Grafico Settimanale
    fig_settimanale = go.Figure(data=[
        go.Bar(x=data.index, y=data['Rendimento_Settimanale']*100,
               name="Rendimento Settimanale", marker_color='green')
    ])
    fig_settimanale.update_layout(
        title=f"Rendimento Settimanale ({selected_ticker})",
        xaxis_title="Anno",
        yaxis_title="Rendimento (%)",
        height=500,
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        font=dict(color='white')
    )

    # Grafico Mensile
    fig_mensile = go.Figure(data=[
        go.Bar(x=data.index, y=data['Rendimento_Mensile']*100,
               name="Rendimento Mensile", marker_color='orange')
    ])
    fig_mensile.update_layout(
        title=f"Rendimento Mensile ({selected_ticker})",
        xaxis_title="Anno",
        yaxis_title="Rendimento (%)",
        height=500,
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        font=dict(color='white')
    )

    # Grafico Volatilità
    fig_vol = go.Figure(data=[
        go.Scatter(x=data.index, y=data['Volatilità_Giornaliera'],
                   mode='lines', name="Volatilità Annualizzata",
                   line=dict(color='red'))
    ])
    fig_vol.update_layout(
        title=f"Volatilità ({selected_ticker})",
        xaxis_title="Data",
        yaxis_title="Volatilità",
        height=500,
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        font=dict(color='white')
    )

    return (fig_giornaliero, fig_settimanale, fig_mensile,
            fig_vol, warning_message, "")

if __name__ == '__main__':
    app.run_server(debug=True)

