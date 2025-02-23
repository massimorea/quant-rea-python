# ricerca.py

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

def load_tickers_from_csv(path="all_tickers.csv"):
    """
    Legge un CSV con colonne: [Mercato, Ticker, Descrizione, Exchange]
    e crea una lista di opzioni per il dropdown, del tipo:
    {
      'label': 'BABA - Alibaba Group Holding (NYSE)',
      'value': 'NYSE:BABA'
    }
    """
    df = pd.read_csv(path)
    options = []
    for _, row in df.iterrows():
        ticker = str(row['Ticker'])
        descr = str(row['Descrizione'])
        exch  = str(row['Exchange'])
        label = f"{ticker} - {descr} ({exch})"  # testo mostrato all'utente
        value = f"{exch}:{ticker}"             # valore usato da tvDatafeed
        options.append({'label': label, 'value': value})
    return options

def get_search_layout():
    """
    Restituisce un layout con UN dropdown "searchable" che mostra
    Ticker - Descrizione (Exchange) e permette la ricerca interna.
    """
    # Carichiamo i ticker dal CSV (una sola volta)
    all_ticker_options = load_tickers_from_csv()

    return html.Div([
        html.Label("Seleziona un Ticker:", style={'color': 'white'}),
        dcc.Dropdown(
            id='search-dropdown',
            options=all_ticker_options,
            value=None,
            placeholder="Digita per cercare un ticker...",
            clearable=True,
            searchable=True,   # <-- ricerca interna
            style={
                'width': '400px',
                'color': 'black',           # testo nel dropdown
                'backgroundColor': 'white'  # sfondo
            }
        )
    ], style={'textAlign': 'center', 'marginBottom': '20px'})

def register_search_callbacks(app):
    """
    Se vuoi definire callback aggiuntivi per filtrare
    dinamicamente, potresti farlo qui. Ma con 'searchable=True'
    non è strettamente necessario.
    """
    pass
