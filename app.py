import dash
from dash import html, dcc
from flask import Flask
import os



# Inizializzazione del server Flask e Dash
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

from ricerca import register_search_callbacks
register_search_callbacks(app)

# Importa le app dei worker
import rendimenti_volatilita
rendimenti_volatilita.register_callbacks(app)  # ✅ Ora i callback sono nel server principale


import rendimenti_asset
rendimenti_asset.register_callbacks(app)  # ✅ Ora i callback sono nel server principale

# Layout base di Dash
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
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
                dcc.Link('Analisi Asset', href='/asset'),
                html.Br(),
                dcc.Link('Analisi Volatilità', href='/volatilita')
            ])
        ])
    elif pathname == '/asset':
        return rendimenti_asset.layout
    elif pathname == '/volatilita':
        return rendimenti_volatilita.layout
    else:
        return '404 - Pagina non trovata'

# Registra i callback delle altre app
app.callback_map.update(rendimenti_volatilita.app.callback_map)
app.callback_map.update(rendimenti_asset.app.callback_map)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run_server(host='0.0.0.0', port=port)
