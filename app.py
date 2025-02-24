import dash
from dash import html, dcc
from flask import Flask, request, jsonify
import os
from urllib.parse import urlparse, parse_qs

# Inizializzazione del server Flask e Dash
server = Flask(__name__)
app = dash.Dash(__name__, server=server, url_base_pathname='/')

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
            dcc.Link('Analisi Asset', href='/asset'),
            html.Br(),
            dcc.Link('Analisi Volatilità', href='/volatilita')
        ])
    elif pathname == '/asset':
        # Importa e ritorna il layout dell'app asset
        from rendimenti_asset import app as asset_app
        return asset_app.layout
    elif pathname == '/volatilita':
        # Importa e ritorna il layout dell'app volatilità
        from rendimenti_volatilita import app as vol_app
        return vol_app.layout
    else:
        return '404 - Pagina non trovata'

# Route per l'API REST
@server.route('/api/asset', methods=['POST'])
def api_asset():
    try:
        data = request.get_json()
        if not data or 'ticker' not in data:
            return jsonify({'error': 'Ticker non specificato'}), 400
        
        # Qui puoi aggiungere la logica per processare l'asset
        # Per esempio, chiamare funzioni dal tuo rendimenti-asset.py
        return jsonify({
            'status': 'success',
            'message': f'Analisi asset avviata per {data["ticker"]}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@server.route('/api/volatilita', methods=['POST'])
def api_volatilita():
    try:
        data = request.get_json()
        if not data or 'ticker' not in data:
            return jsonify({'error': 'Ticker non specificato'}), 400
        
        # Qui puoi aggiungere la logica per processare la volatilità
        # Per esempio, chiamare funzioni dal tuo rendimenti-volatilita.py
        return jsonify({
            'status': 'success',
            'message': f'Analisi volatilità avviata per {data["ticker"]}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Gestione degli errori
@server.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Risorsa non trovata'}), 404

@server.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Errore interno del server'}), 500

# Configurazione del server
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # In produzione (Heroku)
    if os.environ.get("ENVIRONMENT") == "production":
        server.run(host='0.0.0.0', port=port)
    else:
        # In sviluppo locale
        app.run_server(debug=True, port=port)
