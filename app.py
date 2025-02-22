import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import yfinance as yf

# Scarica i dati di Bitcoin
btc_data = yf.download('BTC-USD')

# Calcola i rendimenti giornalieri, settimanali e mensili
btc_data['Rendimento_Giornaliero'] = btc_data['Close'].pct_change()
btc_data['Rendimento_Settimanale'] = btc_data['Close'].resample('W').ffill().pct_change()
btc_data['Rendimento_Mensile'] = btc_data['Close'].resample('ME').ffill().pct_change()

# Calcola la volatilità giornaliera (su una finestra di 30 giorni)
btc_data['Volatilità_Giornaliera'] = btc_data['Rendimento_Giornaliero'].rolling(window=30).std() * np.sqrt(365)

# Creazione dell'app Dash
app = dash.Dash(__name__)
server = app.server  # Necessario per Gunicorn su Heroku

# Layout della Dashboard
app.layout = html.Div(children=[
    html.H1("QUANT-REA: Analisi Volatilità Bitcoin", style={'textAlign': 'center'}),

    html.H3("Rendimenti Annualizzati"),
    dcc.Graph(
        id='grafico-rendimenti-mensili',
        figure={
            'data': [
                go.Bar(
                    x=btc_data['Rendimento_Mensile'].groupby(btc_data.index.year).mean().index,
                    y=btc_data['Rendimento_Mensile'].groupby(btc_data.index.year).mean() * 100,
                    name="Rendimento Mensile",
                    marker_color='blue'
                )
            ],
            'layout': go.Layout(
                title="Rendimento Mensile Annualizzato",
                xaxis={'title': "Anno"},
                yaxis={'title': "Rendimento (%)"},
                height=500
            )
        }
    ),

    html.H3("Volatilità Bitcoin"),
    dcc.Graph(
        id='grafico-volatilita',
        figure={
            'data': [
                go.Scatter(
                    x=btc_data.index,
                    y=btc_data['Volatilità_Giornaliera'],
                    mode='lines',
                    name="Volatilità Annualizzata",
                    line=dict(color='orange')
                )
            ],
            'layout': go.Layout(
                title="Volatilità Annualizzata di Bitcoin",
                xaxis={'title': "Data"},
                yaxis={'title': "Volatilità"},
                height=500
            )
        }
    )
])

# Esegui l'applicazione
if __name__ == '__main__':
    app.run_server(debug=True)
