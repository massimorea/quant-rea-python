import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
import pandas as pd

def load_tickers_from_csv(path="all_tickers.csv"):
    """ Carica il CSV con i ticker. """
    return pd.read_csv(path)

def get_search_layout():
    """ Layout con dropdown per la ricerca. """
    return html.Div([
        html.Label("Seleziona un Ticker:", style={'color': 'white'}),
        dcc.Dropdown(
            id='search-dropdown',
            options=[],
            value=None,
            placeholder="Digita almeno 3 caratteri per cercare...",
            clearable=True,  # Cambiato da False a True
            searchable=True,
            style={'width': '700px', 'color': 'black', 'backgroundColor': 'white', 'margin': 'auto'}
        ),
        html.Div(id='search-status', style={'color': 'yellow', 'marginTop': '5px', 'textAlign': 'center'}),
    ], style={'textAlign': 'center', 'marginBottom': '20px'})

def register_search_callbacks(app):
    """ Callback per aggiornare il dropdown e salvare il ticker selezionato. """
    
    @app.callback(
        [dd.Output('search-dropdown', 'options'),
         dd.Output('search-status', 'children')],
        [dd.Input('search-dropdown', 'search_value')]
    )
    def update_dropdown_options(search_value):
        if not search_value or len(search_value) < 3:
            return [], "Digita almeno 3 caratteri per cercare..."
        
        df = load_tickers_from_csv()
        mask = (df['Ticker'].str.contains(search_value, case=False, na=False) |
                df['Descrizione'].str.contains(search_value, case=False, na=False))
        filtered_df = df[mask]
        
        if filtered_df.empty:
            return [], "⚠️ Nessun risultato trovato."
        
        options = [{'label': f"{row['Ticker']} - {row['Descrizione']} ({row['Exchange']})", 
                    'value': f"{row['Exchange']}:{row['Ticker']}"} for _, row in filtered_df.iterrows()]
        return options, ""

    @app.callback(
        [dd.Output('selected-ticker', 'value'),
         dd.Output('search-dropdown', 'value')],
        [dd.Input('search-dropdown', 'value')],
        [dd.State('selected-ticker', 'value')],
        prevent_initial_call=True
    )
    def update_selected_ticker(dropdown_value, current_ticker):
        if dropdown_value is None:
            # Se il dropdown è vuoto, mantieni l'ultimo valore valido
            return current_ticker or "", current_ticker or ""
        
        # Assicurati che il valore non sia vuoto
        if dropdown_value.strip() == "":
            return current_ticker or "", current_ticker or ""
            
        print(f"🔍 DEBUG: Aggiornamento ticker da {current_ticker} a {dropdown_value}")
        return dropdown_value, dropdown_value
