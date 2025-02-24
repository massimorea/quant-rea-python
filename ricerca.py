import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
import pandas as pd
from dash.exceptions import PreventUpdate

def load_tickers_from_csv(path="all_tickers.csv"):
    """ Carica il CSV con i ticker. """
    return pd.read_csv(path)

def get_search_layout():
    """ Layout con dropdown per la ricerca. """
    return html.Div([
        html.Label("Seleziona un Asset Ticker / Nome dell'azienda:", style={'color': 'white'}),
        dcc.Dropdown(
            id='search-dropdown',
            options=[],
            value=None,
            placeholder="Digita almeno 3 caratteri per cercare...",
            clearable=True,
            searchable=True,
            persistence=True,  # Mantiene il valore anche dopo il refresh
            persistence_type='session',  # Salva nella sessione del browser
            style={'width': '700px', 'color': 'black', 'backgroundColor': 'white', 'margin': 'auto'}
        ),
        html.Div(id='search-status', style={'color': 'yellow', 'marginTop': '5px', 'textAlign': 'center'}),
        html.Label("se hai il ticker esatto:", style={'color': 'white'}),
        dcc.Input(
            id='selected-ticker',
            type='text',
            value="",
            persistence=True,  # Mantiene il valore anche dopo il refresh
            persistence_type='session',  # Salva nella sessione del browser
            style={'display': 'inline-block', 'backgroundColor': 'grey'}
        ),
        # Aggiungiamo un div per il debug
        html.Div(id='debug-info', style={'color': 'yellow', 'fontSize': '12px', 'marginTop': '5px'})
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
         dd.Output('search-dropdown', 'value'),
         dd.Output('debug-info', 'children')],
        [dd.Input('search-dropdown', 'value'),
         dd.Input('selected-ticker', 'value')],
        prevent_initial_call=True
    )
    def update_selected_ticker(dropdown_value, manual_value):
        # Identifica quale input ha triggato il callback
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
            
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        debug_msg = f"Trigger: {trigger_id}"
        
        try:
            if trigger_id == 'search-dropdown':
                if dropdown_value is None or dropdown_value.strip() == "":
                    debug_msg += " | Dropdown vuoto"
                    return manual_value or "", "", debug_msg
                
                debug_msg += f" | Nuovo valore: {dropdown_value}"
                return dropdown_value, dropdown_value, debug_msg
                
            elif trigger_id == 'selected-ticker':
                if manual_value and manual_value.strip():
                    debug_msg += f" | Input manuale: {manual_value}"
                    return manual_value, manual_value, debug_msg
                    
            # Se arriviamo qui, qualcosa non va come previsto
            debug_msg += " | Nessuna azione valida"
            raise PreventUpdate
            
        except Exception as e:
            debug_msg += f" | Errore: {str(e)}"
            print(f"❌ Errore nel callback: {str(e)}")
            return "", "", debug_msg

    # Callback aggiuntivo per sincronizzare i valori
    @app.callback(
        dd.Output('selected-ticker', 'value', allow_duplicate=True),
        [dd.Input('search-dropdown', 'value')],
        prevent_initial_call=True
    )
    def sync_values(dropdown_value):
        if dropdown_value is None or dropdown_value.strip() == "":
            raise PreventUpdate
        return dropdown_value
