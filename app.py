from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from flask import jsonify
from flask_cors import CORS
import redis
import os
from ricerca import get_search_layout, register_search_callbacks

# Inizializza l'app
app = Dash(__name__, 
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True
)

# Configurazione server
server = app.server
CORS(server)  # Abilita CORS per le chiamate cross-origin

# Setup Redis per comunicare con i worker (se usi Redis)
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_client = redis.from_url(redis_url)

# Layout principale
app.layout = html.Div([
    dcc.Store(id='memory'),
    html.H1('Quant REA Dashboard', 
        style={'textAlign': 'center', 'color': 'white', 'marginTop': '20px'}
    ),
    get_search_layout(),
    html.Div(id='output-container')
])

# Endpoint per i worker
@server.route('/api/rendimenti', methods=['POST'])
def trigger_rendimenti():
    try:
        # Pubblica un messaggio per il worker rendimenti
        redis_client.publish('calcola-rendimenti', 'start')
        return jsonify({
            "status": "success",
            "message": "Calcolo rendimenti avviato"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@server.route('/api/volatilita', methods=['POST'])
def trigger_volatilita():
    try:
        # Pubblica un messaggio per il worker volatilità
        redis_client.publish('calcola-volatilita', 'start')
        return jsonify({
            "status": "success",
            "message": "Calcolo volatilità avviato"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Endpoint per verificare lo stato dei worker
@server.route('/api/status', methods=['GET'])
def check_status():
    try:
        rendimenti_status = redis_client.get('rendimenti-status') or b'idle'
        volatilita_status = redis_client.get('volatilita-status') or b'idle'
        
        return jsonify({
            "rendimenti": rendimenti_status.decode('utf-8'),
            "volatilita": volatilita_status.decode('utf-8')
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Registra i callback della ricerca
register_search_callbacks(app)

# Callback per aggiornare l'output container
@app.callback(
    Output('output-container', 'children'),
    [Input('memory', 'data')]
)
def update_output(data):
    if not data:
        return html.Div("Seleziona un asset per visualizzare i dati")
    return html.Div(f"Dati per: {data}")

if __name__ == '__main__':
    app.run_server(debug=True)
