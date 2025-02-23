# ricerca.py

import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
import pandas as pd

def load_tickers_df(path="all_tickers.csv"):
    """
    Carica il CSV con le colonne: Mercato, Ticker, Descrizione, Exchange.
    Restituisce un DataFrame.
    """
    df = pd.read_csv(path)
    return df

# Carica i ticker in un DataFrame globale (viene fatto una volta sola all'avvio)
df_tickers = load_tickers_df()

def search_tickers(search_value):
    """
    Filtra il DataFrame in base a search_value su Ticker, Descrizione o Exchange.
    Restituisce una lista di opzioni per il Dropdown.
    Ogni opzione è un dict:
      {'label': 'Ticker - Descrizione (Exchange)', 'value': 'Exchange:Ticker'}
    """
    if not search_value:
        return []
    mask = (
        df_tickers['Ticker'].str.contains(search_value, case=False, na=False) |
        df_tickers['Descrizione'].str.contains(search_value, case=False, na=False) |
        df_tickers['Exchange'].str.contains(search_value, case=False, na=False)
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
    return options

def get_search_layout():
    """
    Restituisce un layout con un UNICO dropdown (ricercabile) che mostra le opzioni
    basate sui ticker caricati dal CSV.
    """
    return html.Div([
        html.Label("Seleziona un Ticker:", style={'color': 'white'}),
        dcc.Dropdown(
            id='search-dropdown',
            options=[],  # Le opzioni saranno aggiornate dinamicamente via callback
            value=None,
            placeholder="Digita per cercare un ticker...",
            clearable=True,
            searchable=True,
            style={
                'width': '400px',
                'color': 'black',          # testo interno nero
                'backgroundColor': 'white' # sfondo bianco
            }
        )
    ], style={'textAlign': 'center', 'marginBottom': '20px'})

def register_search_callbacks(app):
    """
    Registra un callback per aggiornare le opzioni del dropdown in base a quanto l'utente digita.
    Utilizza la proprietà 'search_value' del dropdown.
    """
    @app.callback(
        dd.Output('search-dropdown', 'options'),
        [dd.Input('search-dropdown', 'search_value')]
    )
    def update_dropdown_options(search_value):
        return search_tickers(search_value)

