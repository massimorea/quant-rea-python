import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
from dash.exceptions import PreventUpdate
import pandas as pd
import dash

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
            clearable=False,  # Cambiato a False
            searchable=True,
            persistence=True,  # Aggiunto persistence
            persistence_type='session',
            style={'width': '700px', 'color': 'black', 'backgroundColor': 'white', 'margin': 'auto'}
        ),
        html.Div(id='search-status', style={'color': 'yellow', 'marginTop': '5px', 'textAlign': 'center'}),
        html.Label("se hai il ticker esatto:", style={'color': 'white'}),
        dcc.Input(
            id='selected-ticker',
            type='text',
            value="",
            persistence=True,  # Aggiunto persistence
            persistence_type='session',
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
        print(f"🔍 DEBUG update_dropdown_options - search_value: {search_value}")
        
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
        print(f"📊 DEBUG: Generati {len(options)} opzioni")
        return options, ""

    @app.callback(
        [dd.Output('selected-ticker', 'value'),
         dd.Output('debug-info', 'children')],
        [dd.Input('search-dropdown', 'value')],
        [dd.State('selected-ticker', 'value')],
        prevent_initial_call=True
    )
    def update_selected_ticker(dropdown_value, current_value):
        ctx = dash.callback_context
        if not ctx.triggered:
            print("⚠️ DEBUG: Nessun trigger")
            raise PreventUpdate
            
        trigger = ctx.triggered[0]
        print(f"🎯 DEBUG Trigger: {trigger['prop_id']}")
        print(f"📝 DEBUG Dropdown value: {dropdown_value}")
        print(f"📝 DEBUG Current value: {current_value}")

        # Se il dropdown ha un valore valido, usalo
        if dropdown_value:
            print(f"✅ DEBUG: Nuovo valore dal dropdown: {dropdown_value}")
            return dropdown_value, f"Ticker selezionato: {dropdown_value}"
            
        # Se il dropdown è None ma abbiamo un valore corrente, mantienilo
        if current_value:
            print(f"🔄 DEBUG: Mantengo valore corrente: {current_value}")
            return current_value, f"Ticker mantenuto: {current_value}"
            
        print("⚠️ DEBUG: Nessun valore valido")
        return "", "In attesa di selezione..."

    # Callback per sincronizzare il dropdown con l'input manuale
    @app.callback(
        dd.Output('search-dropdown', 'value'),
        [dd.Input('selected-ticker', 'value')],
        [dd.State('search-dropdown', 'value')],
        prevent_initial_call=True
    )
    def sync_dropdown_with_input(manual_value, current_dropdown):
        print(f"✍️ DEBUG sync_dropdown - manual: {manual_value}, current: {current_dropdown}")
        
        if not manual_value and current_dropdown:
            print(f"🔄 DEBUG: Mantengo valore dropdown: {current_dropdown}")
            return current_dropdown
            
        if manual_value:
            print(f"✅ DEBUG: Aggiorno dropdown con: {manual_value}")
            return manual_value
            
        raise PreventUpdate
