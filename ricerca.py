import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

# Lista di ticker di esempio; in un progetto reale potresti caricarla da un CSV o DB
ALL_TICKERS = [
    "BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:BNBUSDT",
    "NASDAQ:AAPL", "NASDAQ:TSLA", "NASDAQ:MSFT",
    "NYSE:BA", "NYSE:KO", "NYSE:GE"
]

def get_search_layout():
    """Ritorna il layout per la ricerca con input e dropdown."""
    return html.Div([
        html.Label("Inserisci un ticker TradingView (es. BINANCE:BTCUSDT, NASDAQ:AAPL):", style={'color': 'white'}),
        dcc.Input(id='search-input', type='text', value='', debounce=True, style={'marginLeft': '10px', 'width': '250px'}),
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
    """Registra il callback per aggiornare il dropdown filtrando ALL_TICKERS."""
    @app.callback(
        dd.Output('search-dropdown', 'options'),
        [dd.Input('search-input', 'value')]
    )
    def update_dropdown_options(search_value):
        if not search_value:
            return []
        filtered = [t for t in ALL_TICKERS if search_value.upper() in t.upper()]
        return [{'label': t, 'value': t} for t in filtered]
