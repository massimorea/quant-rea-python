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

# Layout della Dashboard con tema scuro
app.layout = html.Div(style={'backgroundColor': '#121212', 'color': '#FFFFFF', 'fontFamily': 'Arial, sans-serif'}, children=[
    html.H1("QUANT-REA: Analisi Volatilità Bitcoin", style={'textAlign': 'center', 'color': '#76D7C4'}),

    html.H3("Rendimenti Annualizzati", style={'color': '#FFFFFF'}),
    dcc.Graph(
        id='grafico-rendimenti-mensili',
        figure={
            'data': [
                go.Bar(
                    x=btc_data['Rendimento_Mensile'].groupby(btc_data.index.year).mean().index,
                    y=btc_data['Rendimento_Mensile'].groupby(btc_data.index.year).mean() * 100,
                    name="Rendimento Mensile",
                    marker_color='#2E86C1'  # Blu più adatto al tema Quant-Rea
                )
            ],
            'layout': go.Layout(
                title="Rendimento Mensile Annualizzato",
                plot_bgcolor='#1F1F1F',  # Sfondo grafico scuro
                paper_bgcolor='#121212',  # Sfondo scuro coerente
                font=dict(color='#FFFFFF'),  # Testo bianco per visibilità
                xaxis={'title': "Anno", 'color': '#FFFFFF'},
                yaxis={'title': "Rendimento (%)", 'color': '#FFFFFF'},
                height=500
            )
        }
    ),

    html.H3("Volatilità Bitcoin", style={'color': '#FFFFFF'}),
    dcc.Graph(
        id='grafico-volatilita',
        figure={
            'data': [
                go.Scatter(
                    x=btc_data.index,
                    y=btc_data['Volatilità_Giornaliera'],
                    mode='lines',
                    name="Volatilità Annualizzata",
                    line=dict(color='#FFA500')  # Arancione più in linea con il tema Quant-Rea
                )
            ],
            'layout': go.Layout(
                title="Volatilità Annualizzata di Bitcoin",
                plot_bgcolor='#1F1F1F',  # Sfondo grafico scuro
                paper_bgcolor='#121212',  # Sfondo della pagina scuro
                font=dict(color='#FFFFFF'),  # Testo bianco
                xaxis={'title': "Data", 'color': '#FFFFFF'},
                yaxis={'title': "Volatilità", 'color': '#FFFFFF'},
                height=500
            )
        }
    )
])

# Esegui l'applicazione
if __name__ == '__main__':
    app.run_server(debug=True)

