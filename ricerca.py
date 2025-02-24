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
        dcc.Store(id='ticker-store', storage_type='memory'),  # Store per debug
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
        html.Div(id='debug-info', style={'color': 'yellow', 'fontSize': '12px', 'marginTop': '5px'}),
        # Aggiungiamo più div per il debug
        html.Div(id='debug-dropdown-value', style={'color': 'orange', 'fontSize': '12px'}),
        html.Div(id='debug-store-value', style={'color': 'orange', 'fontSize': '12px'}),
        html.Div(id='debug-selected-value', style={'color': 'orange', 'fontSize': '12px'})
    ], style={'textAlign': 'center', 'marginBottom': '20px'})

def register_search_callbacks(app):
    @app.callback(
        [dd.Output('search-dropdown', 'options'),
         dd.Output('search-status', 'children'),
         dd.Output('debug-dropdown-value', 'children')],
        [dd.Input('search-dropdown', 'search_value')]
    )
    def update_dropdown_options(search_value):
        print(f"🔍 DEBUG update_dropdown_options - search_value: {search_value}")
        
        if not search_value or len(search_value) < 3:
            return [], "Digita almeno 3 caratteri per cercare...", "Ricerca: attendo 3+ caratteri"
        
        df = load_tickers_from_csv()
        mask = (df['Ticker'].str.contains(search_value, case=False, na=False) |
                df['Descrizione'].str.contains(search_value, case=False, na=False))
        filtered_df = df[mask]
        
        if filtered_df.empty:
            return [], "⚠️ Nessun risultato trovato.", f"Nessun risultato per: {search_value}"
        
        options = [{'label': f"{row['Ticker']} - {row['Descrizione']} ({row['Exchange']})", 
                    'value': f"{row['Exchange']}:{row['Ticker']}"} for _, row in filtered_df.iterrows()]
        return options, "", f"Trovati {len(options)} risultati per: {search_value}"

    @app.callback(
        [dd.Output('ticker-store', 'data'),
         dd.Output('debug-store-value', 'children')],
        [dd.Input('search-dropdown', 'value')],
        prevent_initial_call=True
    )
    def store_selected_value(value):
        print(f"💾 DEBUG store_selected_value - value ricevuto: {value}")
        if value is None:
            raise PreventUpdate
        return value, f"Store aggiornato con: {value}"

    @app.callback(
        [dd.Output('selected-ticker', 'value'),
         dd.Output('debug-info', 'children'),
         dd.Output('debug-selected-value', 'children')],
        [dd.Input('ticker-store', 'data')],
        prevent_initial_call=True
    )
    def update_selected_ticker(stored_value):
        print(f"📝 DEBUG update_selected_ticker - stored_value: {stored_value}")
        if stored_value is None:
            raise PreventUpdate
            
        return stored_value, f"Ticker selezionato: {stored_value}", f"Selected-ticker aggiornato con: {stored_value}"

    # Callback per gestire l'input manuale
    @app.callback(
        [dd.Output('ticker-store', 'data', allow_duplicate=True),
         dd.Output('debug-store-value', 'children', allow_duplicate=True)],
        [dd.Input('selected-ticker', 'value')],
        prevent_initial_call=True
    )
    def handle_manual_input(manual_value):
        print(f"✍️ DEBUG handle_manual_input - manual_value: {manual_value}")
        if not manual_value:
            raise PreventUpdate
        return manual_value, f"Store aggiornato manualmente con: {manual_value}"
