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
        dcc.Store(id='ticker-store', storage_type='memory'),
        dcc.Dropdown(
            id='search-dropdown',
            options=[],
            value=None,
            placeholder="Digita almeno 3 caratteri per cercare...",
            clearable=False,  # Cambiato a False per evitare il reset
            searchable=True,
            persistence=True,  # Aggiunto per mantenere il valore
            persistence_type='session',  # Mantiene il valore nella sessione
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
         dd.Output('search-status', 'children'),
         dd.Output('search-dropdown', 'value')],  # Aggiunto per mantenere il valore
        [dd.Input('search-dropdown', 'search_value'),
         dd.State('search-dropdown', 'value')]  # Aggiunto per accedere al valore corrente
    )
    def update_dropdown_options(search_value, current_value):
        if not search_value or len(search_value) < 3:
            return [], "Digita almeno 3 caratteri per cercare...", current_value  # Mantiene il valore corrente
        
        df = load_tickers_from_csv()
        mask = (df['Ticker'].str.contains(search_value, case=False, na=False) |
                df['Descrizione'].str.contains(search_value, case=False, na=False))
        filtered_df = df[mask]
        
        if filtered_df.empty:
            return [], "⚠️ Nessun risultato trovato.", current_value  # Mantiene il valore corrente
        
        options = [{'label': f"{row['Ticker']} - {row['Descrizione']} ({row['Exchange']})", 
                    'value': f"{row['Exchange']}:{row['Ticker']}"} for _, row in filtered_df.iterrows()]
        return options, "", current_value  # Mantiene il valore corrente

    @app.callback(
        [dd.Output('selected-ticker', 'value'),
         dd.Output('debug-info', 'children')],
        [dd.Input('search-dropdown', 'value')],
        prevent_initial_call=True
    )
    def update_selected_ticker(dropdown_value):
        if dropdown_value is None:
            raise PreventUpdate
            
        print(f"📍 Aggiornando selected-ticker con: {dropdown_value}")
        return dropdown_value, f"Ticker selezionato: {dropdown_value}"

    # Callback per gestire l'input manuale
    @app.callback(
        dd.Output('search-dropdown', 'value', allow_duplicate=True),
        [dd.Input('selected-ticker', 'value')],
        prevent_initial_call=True
    )
    def sync_dropdown_with_input(manual_value):
        if not manual_value:
            raise PreventUpdate
        print(f"✍️ Sincronizzando dropdown con input manuale: {manual_value}")
        return manual_value
