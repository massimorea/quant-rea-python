import os
import dash
from dash import dcc, html
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
import numpy as np

# Inizializza l'app Dash
app = dash.Dash(__name__)
server = app.server  # Per Heroku

# Scarica i dati storici di Bitcoin
btc_data = yf.download('BTC-USD')

# Calcola i rendimenti giornalieri
btc_data['Rendimento_Giornaliero'] = btc_data['Close'].pct_change()

# Crea il grafico con stile dark
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=btc_data.index, 
    y=btc_data['Close'], 
    mode='lines', 
    name='BTC-USD',
    line=dict(color='#1f77b4')  # Blu per il tema scuro
))

# Personalizzazione dello sfondo e asse
fig.update_layout(
    plot_bgcolor='#1F1F1F',  # Sfondo del grafico scuro
    paper_bgcolor='#121212',  # Sfondo della pagina
    font=dict(color='#FFFFFF'),  # Testo bianco
    xaxis=dict(gridcolor='#444444'),  # Griglia scura
    yaxis=dict(gridcolor='#444444')
)

# Layout della pagina con tema scuro
app.layout = html.Div(style={'backgroundColor': '#121212', 'color': '#FFFFFF', 'padding': '20px'}, children=[
    html.H1("Bitcoin Price Chart", style={'textAlign': 'center', 'color': '#76D7C4'}),
    dcc.Graph(figure=fig)
])

if __name__ == "__main__":
    app.run_server(debug=True)

