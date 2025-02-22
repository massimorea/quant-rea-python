import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import yfinance as yf

# Creazione dell'app Dash
app = dash.Dash(__name__)
server = app.server  # Necessario per Heroku

# Layout della Dashboard con barra di ricerca
app.layout = html.Div(style={'backgroundColor': '#121212', 'color': 'white', 'padding': '20px'}, children=[
    html.H1("QUANT-REA: Analisi Volatilità Mercato", style={'textAlign': 'center', 'color': 'white'}),

    # Barra di ricerca per selezionare l'asset
    html.Div([
        html.Label("Inserisci il ticker dell'asset (esempio: BTC-USD, ^GSPC, GC=F):", style={'fontSize': '18px'}),
        dcc.Input(id="ticker-input", type="text", value="BTC-USD", debounce=True, style={'marginRight': '10px'}),
        html.Button("Aggiorna Grafici", id="update-button", n_clicks=0, style={'backgroundColor': '#1E90FF', 'color': 'white', 'border': 'none', 'padding': '10px', 'cursor': 'pointer'}),
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),

    # Grafico Rendimenti Mensili
    dcc.Graph(id='grafico-rendimenti-mensili'),

    # Grafico Rendimenti Settimanali
    dcc.Graph(id='grafico-rendimenti-settimanali'),

    # Grafico Volatilità
    dcc.Graph(id='grafico-volatilita')
])

# Funzione per scaricare i dati da Yahoo Finance
def scarica_dati(ticker):
    df = yf.download(ticker)
    df['Rendimento_Giornaliero'] = df['Close'].pct_change()
    df['Rendimento_Settimanale'] = df['Close'].resample('W').ffill().pct_change()
    df['Rendimento_Mensile'] = df['Close'].resample('ME').ffill().pct_change()
    df['Volatilità_Giornaliera'] = df['Rendimento_Giornaliero'].rolling(window=30).std() * np.sqrt(365)
    return df

# Callback per aggiornare i grafici quando si cambia asset
@app.callback(
    [
        dd.Output('grafico-rendimenti-mensili', 'figure'),
        dd.Output('grafico-rendimenti-settimanali', 'figure'),
        dd.Output('grafico-volatilita', 'figure')
    ],
    [dd.Input('update-button', 'n_clicks')],
    [dd.State('ticker-input', 'value')]
)
def aggiorna_grafici(n_clicks, ticker):
    df = scarica_dati(ticker)

    # Grafico Rendimenti Mensili
    fig_rendimenti_mensili = go.Figure()
    fig_rendimenti_mensili.add_trace(go.Bar(
        x=df['Rendimento_Mensile'].groupby(df.index.year).mean().index,
        y=df['Rendimento_Mensile'].groupby(df.index.year).mean() * 100,
        name="Rendimento Mensile",
        marker_color='blue'
    ))
    fig_rendimenti_mensili.update_layout(title="Rendimento Mensile Annualizzato", xaxis_title="Anno", yaxis_title="Rendimento (%)", plot_bgcolor="#121212", paper_bgcolor="#121212", font_color="white")

    # Grafico Rendimenti Settimanali
    fig_rendimenti_settimanali = go.Figure()
    fig_rendimenti_settimanali.add_trace(go.Bar(
        x=df['Rendimento_Settimanale'].groupby(df.index.year).mean().index,
        y=df['Rendimento_Settimanale'].groupby(df.index.year).mean() * 100,
        name="Rendimento Settimanale",
        marker_color='green'
    ))
    fig_rendimenti_settimanali.update_layout(title="Rendimento Settimanale Annualizzato", xaxis_title="Anno", yaxis_title="Rendimento (%)", plot_bgcolor="#121212", paper_bgcolor="#121212", font_color="white")

    # Grafico Volatilità
    fig_volatilita = go.Figure()
    fig_volatilita.add_trace(go.Scatter(
        x=df.index,
        y=df['Volatilità_Giornaliera'],
        mode='lines',
        name="Volatilità Annualizzata",
        line=dict(color='orange')
    ))
    fig_volatilita.update_layout(title="Volatilità Annualizzata", xaxis_title="Data", yaxis_title="Volatilità", plot_bgcolor="#121212", paper_bgcolor="#121212", font_color="white")

    return fig_rendimenti_mensili, fig_rendimenti_settimanali, fig_volatilita

# Esegui l'app
if __name__ == '__main__':
    app.run_server(debug=True)


# Esegui l'applicazione
if __name__ == '__main__':
    app.run_server(debug=True)

