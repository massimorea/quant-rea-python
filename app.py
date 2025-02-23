# app.py

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval

# Importa layout e (eventuali) callback di ricerca
from ricerca import get_search_layout, register_search_callbacks

app = dash.Dash(__name__)
server = app.server  # Necessario per Heroku

tv = TvDatafeed()

# Layout principale
app.layout = html.Div(style={'backgroundColor': '#121212', 'color': 'white', 'padding': '20px'}, children=[

    html.H1("QUANT-REA: Analisi Volatilità Asset",
            style={'textAlign': 'center', 'color': 'cyan'}),

    # Inseriamo il layout di ricerca dal file ricerca.py
    get_search_layout(),

    # Bottone “Analizza”
    html.Button("Analizza", id='analyze-button', n_clicks=0,
                style={'marginLeft': '10px', 'backgroundColor': 'cyan'}),

    # Messaggi di avviso e caricamento
    html.Div(id='ticker-warning',
             style={'color': 'red', 'marginTop': '5px', 'textAlign': 'center'}),
    html.Div(id='loading-message',
             style={'color': 'yellow', 'marginTop': '10px',
                    'fontSize': '16px', 'fontWeight': 'bold', 'textAlign': 'center'}),

    # Grafici
    dcc.Graph(id='grafico-rendimento-giornaliero'),
    dcc.Graph(id='grafico-rendimento-settimanale'),
    dcc.Graph(id='grafico-rendimento-mensile'),
    dcc.Graph(id='grafico-volatilita')
])

# Se in ricerca.py avessi definito callback aggiuntivi, li registreresti qui
register_search_callbacks(app)

def get_asset_data(ticker):
    """
    Scarica i dati dal ticker selezionato, es: 'NYSE:BABA'.
    Calcola rendimenti e volatilità.
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
    except Exception:
        return None

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

    warning_message = ""

    # Rendimento Giornaliero
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

    # Rendimento Settimanale
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

    # Rendimento Mensile
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

    # Volatilità
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
