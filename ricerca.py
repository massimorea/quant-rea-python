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

# Lista globale delle opzioni (tutti i ticker) non verrà usata direttamente nel dropdown
# ma per il filtraggio dinamico.
ALL_TICKERS_OPTIONS = get_all_ticker_options()

def get_search_layout():
    """
    Restituisce un layout con un UNICO dropdown 'searchable' che mostra le opzioni.
    Il dropdown ha:
      - placeholder "Digita almeno 3 caratteri per cercare..."
      - clearable impostato su False, così il valore selezionato non viene cancellato
    """
    return html.Div([
        html.Label("Seleziona un Ticker:", style={'color': 'white'}),
        dcc.Dropdown(
            id='search-dropdown',
            options=[],  # Verranno aggiornate dinamicamente via callback
            value=None,
            placeholder="Digita almeno 3 caratteri per cercare...",
            clearable=False,  # Mantiene il valore selezionato
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
    Registra un callback per aggiornare dinamicamente le opzioni del dropdown in base al testo digitato.
    Se il testo digitato ha meno di 3 caratteri, viene mostrato un messaggio.
    """
    @app.callback(
        [dd.Output('search-dropdown', 'options'),
         dd.Output('search-status', 'children')],
        [dd.Input('search-dropdown', 'search_value')]
    )
    def update_dropdown_options(search_value):
        if not search_value or len(search_value) < 3:
            return [], "Digita almeno 3 caratteri per cercare..."
        # Filtra le opzioni in base al testo (solo Ticker e Descrizione)
        filtered = [opt for opt in ALL_TICKERS_OPTIONS if search_value.upper() in opt['label'].upper()]
        status_message = ""
        if not filtered:
            status_message = "⚠️ Nessun risultato trovato."
        return filtered, status_message

