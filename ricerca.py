# ricerca.py

import json
import requests
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

def get_tradingview_tickers():
    """
    Scarica i ticker dal mercato 'america' di TradingView (azioni ed ETF USA).
    Usa l'endpoint https://scanner.tradingview.com/america/scan.
    Restituisce una lista di stringhe (es: 'NASDAQ:AAPL', 'NYSE:BA', ecc.).
    """
    url = "https://scanner.tradingview.com/america/scan"
    payload = json.dumps({
        "symbols": {"query": {"types": []}},
        "columns": ["name", "description"]
    })
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        response.raise_for_status()  # solleva eccezione se status != 200
        data = response.json()

        # data["data"] è una lista di dict con chiave "d", es: item["d"] = [SYMBOL, DESCRIPTION, ...]
        # item["d"][0] = 'NASDAQ:AAPL', item["d"][1] = 'Apple Inc'
        # Creiamo un elenco di stringhe come 'NASDAQ:AAPL'
        tickers = []
        for item in data.get("data", []):
            info = item.get("d", [])
            if len(info) >= 2:
                symbol = info[0]  # Esempio: 'NASDAQ:AAPL'
                # description = info[1] # Esempio: 'Apple Inc' (se vuoi usarlo)
                if symbol:
                    tickers.append(symbol)
        return tickers
    except Exception as e:
        print("Errore nel recupero dei ticker:", e)
        return []

# Carichiamo i ticker una sola volta (puoi ricaricarli periodicamente se vuoi)
ALL_TICKERS = get_tradingview_tickers()

def get_search_layout():
    """
    Ritorna il layout per la ricerca con input (dove digiti) e dropdown (che mostra i risultati).
    """
    return html.Div([
        html.Label("Inserisci un ticker TradingView (es. BINANCE:BTCUSDT, NASDAQ:AAPL):", style={'color': 'white'}),
        dcc.Input(id='search-input', type='text', value='', debounce=True,
                  style={'marginLeft': '10px', 'width': '250px'}),
        dcc.Dropdown(
            id='search-dropdown',
            options=[],
            value=None,
            placeholder="Seleziona un ticker",
            clearable=True,
            style={'width': '300px', 'display': 'inline-block', 'marginLeft': '10px'}
        )
    ], style={'textAlign': 'center', 'marginBottom': '20px'})

def register_search_callbacks(app):
    """
    Registra il callback che filtra ALL_TICKERS in base al testo digitato in 'search-input'
    e aggiorna le opzioni di 'search-dropdown'.
    """
    @app.callback(
        dd.Output('search-dropdown', 'options'),
        [dd.Input('search-input', 'value')]
    )
    def update_dropdown_options(search_value):
        if not search_value:
            return []
        # Filtra i ticker che contengono la stringa digitata (case-insensitive)
        filtered = [t for t in ALL_TICKERS if search_value.upper() in t.upper()]
        return [{'label': t, 'value': t} for t in filtered]

