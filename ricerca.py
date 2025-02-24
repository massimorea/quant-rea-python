import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
from dash.exceptions import PreventUpdate
import pandas as pd
import dash
from datetime import datetime

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
        [dd.Input('search-dropdown', 'search_value')],
        [dd.State('search-dropdown', 'options')]
    )
    def update_dropdown_options(search_value, current_options):
        ctx = dash.callback_context
        print(f"\n🔍 DEBUG update_dropdown_options - Timestamp: {datetime.now()}")
        print(f"🔍 DEBUG update_dropdown_options - Trigger completo: {ctx.triggered}")
        print(f"🔍 DEBUG update_dropdown_options - search_value: {search_value}")
        print(f"🔍 DEBUG update_dropdown_options - opzioni correnti: {len(current_options) if current_options else 0}")
        
        # Se non c'è valore di ricerca e abbiamo già delle opzioni, le manteniamo
        if not search_value and current_options:
            print("🔄 DEBUG: Mantengo le opzioni correnti")
            return current_options, "", f"Mantenute {len(current_options)} opzioni correnti"
        
        # Se il valore di ricerca è troppo corto ma abbiamo opzioni, le manteniamo
        if search_value and len(search_value) < 3 and current_options:
            print("🔄 DEBUG: Mantengo le opzioni durante la digitazione")
            return current_options, "Digita almeno 3 caratteri per cercare...", f"Mantenute {len(current_options)} opzioni correnti"
        
        # Se non abbiamo né ricerca valida né opzioni correnti
        if not search_value or len(search_value) < 3:
            return [], "Digita almeno 3 caratteri per cercare...", "Ricerca: attendo 3+ caratteri"
        
        df = load_tickers_from_csv()
        mask = (df['Ticker'].str.contains(search_value, case=False, na=False) |
                df['Descrizione'].str.contains(search_value, case=False, na=False))
        filtered_df = df[mask]
        
        if filtered_df.empty:
            # Se non troviamo risultati ma abbiamo opzioni, manteniamo quelle
            if current_options:
                print("🔄 DEBUG: Mantengo le opzioni - nessun nuovo risultato")
                return current_options, "⚠️ Nessun nuovo risultato trovato.", f"Mantenute {len(current_options)} opzioni correnti"
            return [], "⚠️ Nessun risultato trovato.", f"Nessun risultato per: {search_value}"
        
        options = [{'label': f"{row['Ticker']} - {row['Descrizione']} ({row['Exchange']})", 
                    'value': f"{row['Exchange']}:{row['Ticker']}"} for _, row in filtered_df.iterrows()]
        return options, "", f"Trovati {len(options)} risultati per: {search_value}"

    @app.callback(
        [dd.Output('ticker-store', 'data'),
         dd.Output('debug-store-value', 'children')],
        [dd.Input('search-dropdown', 'value')],
        [dd.State('search-dropdown', 'options'),
         dd.State('ticker-store', 'data')],
        prevent_initial_call=True
    )
    def store_selected_value(value, current_options, current_store):
        ctx = dash.callback_context
        print(f"\n💾 DEBUG store_selected_value - Timestamp: {datetime.now()}")
        print(f"💾 DEBUG store_selected_value - Trigger completo: {ctx.triggered}")
        print(f"💾 DEBUG store_selected_value - Tutti gli inputs: {ctx.inputs}")
        print(f"💾 DEBUG store_selected_value - Tutti gli states: {ctx.states}")
        print(f"💾 DEBUG store_selected_value - value ricevuto: {value}")
        print(f"💾 DEBUG store_selected_value - tipo del value: {type(value)}")
        print(f"💾 DEBUG store_selected_value - opzioni correnti: {len(current_options) if current_options else 0}")
        print(f"💾 DEBUG store_selected_value - valore corrente store: {current_store}")
        
        if value is None:
            print("⚠️ DEBUG store_selected_value - PreventUpdate per value None")
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
        ctx = dash.callback_context
        print(f"\n📝 DEBUG update_selected_ticker - Timestamp: {datetime.now()}")
        print(f"📝 DEBUG update_selected_ticker - Trigger completo: {ctx.triggered}")
        print(f"📝 DEBUG update_selected_ticker - stored_value: {stored_value}")
        print(f"📝 DEBUG update_selected_ticker - tipo dello stored_value: {type(stored_value)}")
        
        if stored_value is None:
            print("⚠️ DEBUG update_selected_ticker - PreventUpdate per stored_value None")
            raise PreventUpdate
            
        return stored_value, f"Ticker selezionato: {stored_value}", f"Selected-ticker aggiornato con: {stored_value}"

    @app.callback(
        [dd.Output('ticker-store', 'data', allow_duplicate=True),
         dd.Output('debug-store-value', 'children', allow_duplicate=True)],
        [dd.Input('selected-ticker', 'value')],
        prevent_initial_call=True
    )
    def handle_manual_input(manual_value):
        ctx = dash.callback_context
        print(f"\n✍️ DEBUG handle_manual_input - Timestamp: {datetime.now()}")
        print(f"✍️ DEBUG handle_manual_input - Trigger completo: {ctx.triggered}")
        print(f"✍️ DEBUG handle_manual_input - manual_value: {manual_value}")
        print(f"✍️ DEBUG handle_manual_input - tipo del manual_value: {type(manual_value)}")
        
        if not manual_value:
            print("⚠️ DEBUG handle_manual_input - PreventUpdate per manual_value vuoto")
            raise PreventUpdate
        return manual_value, f"Store aggiornato manualmente con: {manual_value}"
