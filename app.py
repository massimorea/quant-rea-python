import dash
from dash import html, dcc
from flask import Flask
import os

# Inizializzazione del server Flask e Dash
server = Flask(__name__)
app = dash.Dash(__name__, server=server, url_base_pathname='/')

# Layout base di Dash
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),  # Refresh=True per ricaricare completamente la pagina
    html.Div(id='page-content')
])

# Callback per gestire il routing
@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return html.Div([
            html.H1('QUANT-REA Dashboard'),
            html.P('Seleziona un\'analisi:'),
            html.Div([
                html.A('Analisi Asset', href='/asset', className='button'),
                html.Br(),
                html.A('Analisi Volatilità', href='/volatilita', className='button')
            ])
        ])
    elif pathname == '/asset':
        # Reindirizza all'app asset
        from rendimenti_asset import app as asset_app
        return asset_app.layout
    elif pathname == '/volatilita':
        # Reindirizza all'app volatilità
        from rendimenti_volatilita import app as vol_app
        return vol_app.layout
    else:
        return html.H1('404 - Pagina non trovata')

# Configurazione del server
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    server.run(host='0.0.0.0', port=port)
