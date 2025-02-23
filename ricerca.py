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

# Carica i ticker una sola volta (all'avvio)
df_tickers = load_tickers_from_csv()

def get_search_layout():
    """
    Restituisce un layout contenente un UNICO dropdown 'searchable' che mostra le opzioni
    basate sui ticker caricati dal CSV.
    Le opzioni hanno il formato:
      label: "Ticker - Descrizione (Exchange)"
      value: "Exchange:Ticker"
    """
    return html.Div([
        html.Label("Seleziona un Ticker:", style={'color': 'white'}),
        dcc.Dropdown(
            id='search-dropdown',
            options=[],  # Le opzioni saranno aggiornate dinamicamente via callback
            value=None,
            placeholder="Digita per cercare un ticker...",
            clearable=False,    # Non si svuota, rimane selezionato
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
    Registra un callback che, mentre l'utente digita nel dropdown (usando la proprietà
    'search_value'), aggiorna le opzioni filtrando solo per i campi Ticker e Descrizione.
    Mostra anche un messaggio di stato ("Ricerca in corso..." o "Nessun risultato trovato").
    """
    @app.callback(
        [dd.Output('search-dropdown', 'options'),
         dd.Output('search-status', 'children')],
        [dd.Input('search-dropdown', 'search_value')]
    )
    def update_dropdown_options(search_value):
        if not search_value:
            return [], ""
        # Mostra il messaggio di caricamento
        status_message = "🔍 Ricerca in corso..."
        # Filtra i ticker in base al testo digitato, considerando solo Ticker e Descrizione
        mask = (
            df_tickers['Ticker'].str.contains(search_value, case=False, na=False) |
            df_tickers['Descrizione'].str.contains(search_value, case=False, na=False)
        )
        filtered_df = df_tickers[mask]
        options = []
        for _, row in filtered_df.iterrows():
            ticker = str(row['Ticker'])
            descr = str(row['Descrizione'])
            exch  = str(row['Exchange'])
            label = f"{ticker} - {descr} ({exch})"
            value = f"{exch}:{ticker}"
            options.append({'label': label, 'value': value})
        if not options:
            status_message = "⚠️ Nessun risultato trovato."
        else:
            status_message = ""
        return options, status_message
