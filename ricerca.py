import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
import pandas as pd

def load_tickers_from_csv(path="all_tickers.csv"):
    """
    Legge un CSV con le colonne: [Mercato, Ticker, Descrizione, Exchange]
    e restituisce un DataFrame.
    """
    df = pd.read_csv(path)
    return df

# Carica il CSV in un DataFrame (eseguito una sola volta all'avvio)
df_tickers = load_tickers_from_csv()

def get_all_ticker_options():
    """
    Crea una lista di opzioni per il dropdown.
    Ogni opzione è un dict:
      {'label': "Ticker - Descrizione (Exchange)", 'value': "Exchange:Ticker"}
    """
    options = []
    for _, row in df_tickers.iterrows():
        ticker = str(row['Ticker'])
        descr = str(row['Descrizione'])
        exch  = str(row['Exchange'])
        label = f"{ticker} - {descr} ({exch})"
        value = f"{exch}:{ticker}"
        options.append({'label': label, 'value': value})
    return options

# Lista globale di opzioni (tutti i ticker)
ALL_TICKERS_OPTIONS = get_all_ticker_options()

def get_search_layout():
    """
    Restituisce un layout con un UNICO dropdown 'searchable' che mostra le opzioni.
    Il dropdown ha:
      - placeholder "Digita per cercare un ticker..."
      - clearable impostato su False, così il valore selezionato non viene cancellato
    """
    return html.Div([
        html.Label("Seleziona un Ticker:", style={'color': 'white'}),
        dcc.Dropdown(
            id='search-dropdown',
            options=ALL_TICKERS_OPTIONS,
            value=None,
            placeholder="Digita per cercare un ticker...",
            clearable=False,  # Una volta selezionato, il ticker rimane
            searchable=True,
            style={
                'width': '400px',
                'color': 'black',          # Testo interno nero
                'backgroundColor': 'white' # Sfondo bianco
            }
        ),
        html.Div(id='search-status', style={'color': 'yellow', 'marginTop': '5px', 'textAlign': 'center'})
    ], style={'textAlign': 'center', 'marginBottom': '20px'})

def register_search_callbacks(app):
    """
    Registra il callback per aggiornare dinamicamente le opzioni del dropdown.
    Utilizza la proprietà 'search_value' del dropdown.
    Se l'utente digita, filtra le opzioni in base a Ticker e Descrizione.
    Se non digita nulla, restituisce tutte le opzioni.
    """
    @app.callback(
        [dd.Output('search-dropdown', 'options'),
         dd.Output('search-status', 'children')],
        [dd.Input('search-dropdown', 'search_value')]
    )
    def update_dropdown_options(search_value):
        if not search_value:
            # Se il campo è vuoto, restituisce tutte le opzioni
            return ALL_TICKERS_OPTIONS, ""
        status_message = "🔍 Ricerca in corso..."
        # Filtra solo per Ticker e Descrizione (case-insensitive)
        filtered = [opt for opt in ALL_TICKERS_OPTIONS if search_value.upper() in opt['label'].upper()]
        if not filtered:
            status_message = "⚠️ Nessun risultato trovato."
        else:
            status_message = ""
        return filtered, status_message
