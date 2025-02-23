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

def get_search_layout():
    """
    Restituisce un layout con un UNICO dropdown 'searchable' che
    verrà popolato dinamicamente solo dopo aver digitato almeno 3 caratteri.
    """
    return html.Div([
        html.Label("Seleziona un Ticker:", style={'color': 'white'}),
        dcc.Dropdown(
            id='search-dropdown',
            options=[],  # Le opzioni verranno caricate dinamicamente via callback
            value=None,
            placeholder="Digita almeno 3 caratteri per cercare...",
            clearable=False,  # Il valore selezionato rimane
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
    Carica il CSV solo se l'utente ha digitato almeno 3 caratteri.
    """
    @app.callback(
        [dd.Output('search-dropdown', 'options'),
         dd.Output('search-status', 'children')],
        [dd.Input('search-dropdown', 'search_value')]
    )
    def update_dropdown_options(search_value):
        if not search_value or len(search_value) < 3:
            # Se il testo è vuoto o meno di 3 caratteri, non restituisce opzioni
            return [], "Digita almeno 3 caratteri per cercare..."
        # Carica il CSV in questo callback (on-demand)
        df = load_tickers_from_csv()
        # Filtra solo per i campi Ticker e Descrizione (case-insensitive)
        mask = (
            df['Ticker'].str.contains(search_value, case=False, na=False) |
            df['Descrizione'].str.contains(search_value, case=False, na=False)
        )
        filtered_df = df[mask]
        if filtered_df.empty:
            return [], "⚠️ Nessun risultato trovato."
        options = []
        for _, row in filtered_df.iterrows():
            ticker = str(row['Ticker'])
            descr = str(row['Descrizione'])
            exch  = str(row['Exchange'])
            label = f"{ticker} - {descr} ({exch})"
            value = f"{exch}:{ticker}"
            options.append({'label': label, 'value': value})
        return options, ""
