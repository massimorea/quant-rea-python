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
    Il ticker selezionato viene mostrato in un input nascosto per `app.py`.
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
        html.Div(id='search-status', style={'color': 'yellow', 'marginTop': '5px', 'textAlign': 'center'}),

        # Input nascosto che memorizza il valore selezionato (exchange:ticker)
        dcc.Input(id='selected-ticker', type='text', value="", style={'display': 'none'})
    ], style={'textAlign': 'center', 'marginBottom': '20px'})

def register_search_callbacks(app):
    """
    Registra il callback per aggiornare dinamicamente le opzioni del dropdown.
    Inoltre, aggiorna l'input nascosto `selected-ticker` con il valore selezionato.
    """
    @app.callback(
        [dd.Output('search-dropdown', 'options'),
         dd.Output('search-status', 'children')],
        [dd.Input('search-dropdown', 'search_value')]
    )
    def update_dropdown_options(search_value):
        if not search_value or len(search_value) < 3:
            return [], "Digita almeno 3 caratteri per cercare..."
        
        df = load_tickers_from_csv()
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
            value = f"{exch}:{ticker}"  # Questo è il formato richiesto
            options.append({'label': label, 'value': value})

        return options, ""

    @app.callback(
        dd.Output('selected-ticker', 'value'),
        [dd.Input('search-dropdown', 'value')]
    )
    def update_selected_ticker(selected_value):
        """
        Quando selezioni un asset, lo salva nel campo nascosto `selected-ticker`.
        """
        return selected_value if selected_value else ""

