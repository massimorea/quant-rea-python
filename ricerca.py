import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
from dash.exceptions import PreventUpdate
import pandas as pd

def load_tickers_from_csv(path="all_tickers.csv"):
    """ Carica il CSV con i ticker. """
    return pd.read_csv(path)

def get_search_layout():
    """ Layout con dropdown per la ricerca. """
    return html.Div([
        html.Label("Seleziona un Asset Ticker / Nome dell'azienda:", style={'color': 'white'}),
        dcc.Store(id='ticker-store', storage_type='memory'),  # Aggiungiamo uno store
        dcc.Dropdown(
            id='search-dropdown',
            options=[],
            value=None,
            placeholder="Digita almeno 3 caratteri per cercare...",
            clearable=True,
            searchable=True,
            style={'width': '700px', 'color': 'black', 'backgroundColor': 'white', 'margin': 'auto'}
        ),
        html.Div(id='search-status', style={'color': 'yellow', 'marginTop': '5px', 'textAlign': 'center'}),
        html.Label("se hai il ticker esatto:", style={'color': 'white'}),
        dcc.Input(
            id='selected-ticker',
            type='text',
            value="",
            style={'display': 'inline-block', 'backgroundColor': 'grey'}
        ),
        html.Div(id='debug-info', style={'color': 'yellow', 'fontSize': '12px', 'marginTop': '5px'})
    ], style={'textAlign': 'center', 'marginBottom': '20px'})

def register_search_callbacks(app):
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
        dd.Output('ticker-store', 'data'),
        [dd.Input('search-dropdown', 'value')],
        prevent_initial_call=True
    )
    def store_selected_value(value):
        if value is None:
            raise PreventUpdate
        print(f"🔍 Salvando nel store: {value}")
        return value

    @app.callback(
        [dd.Output('selected-ticker', 'value'),
         dd.Output('debug-info', 'children')],
        [dd.Input('ticker-store', 'data')],
        prevent_initial_call=True
    )
    def update_selected_ticker(stored_value):
        if stored_value is None:
            raise PreventUpdate
            
        print(f"📍 Aggiornando selected-ticker con: {stored_value}")
        return stored_value, f"Ticker selezionato: {stored_value}"

    # Callback per gestire l'input manuale
    @app.callback(
        dd.Output('ticker-store', 'data', allow_duplicate=True),
        [dd.Input('selected-ticker', 'value')],
        prevent_initial_call=True
    )
    def handle_manual_input(manual_value):
        if not manual_value:
            raise PreventUpdate
        print(f"✍️ Input manuale: {manual_value}")
        return manual_value
