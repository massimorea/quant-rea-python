import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
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
            style={'display': 'online','backgroundColor': 'grey'}
        ),
    ], style={'textAlign': 'center', 'marginBottom': '20px'})

def register_search_callbacks(app):
    """ Callback per aggiornare il dropdown e salvare il ticker selezionato. """
    
    @app.callback(
        [dd.Output('search-dropdown', 'options'),
         dd.Output('search-status', 'children')],
        [dd.Input('search-dropdown', 'search_value')]
    )
    def update_dropdown_options(search_value):
        print(f"🔍 DEBUG search_value ricevuto: {search_value}")
        
        if not search_value or len(search_value) < 3:
            print("⚠️ DEBUG: search_value < 3 caratteri")
            return [], "Digita almeno 3 caratteri per cercare..."
        
        df = load_tickers_from_csv()
        mask = (df['Ticker'].str.contains(search_value, case=False, na=False) |
                df['Descrizione'].str.contains(search_value, case=False, na=False))
        filtered_df = df[mask]
        
        if filtered_df.empty:
            print("❌ DEBUG: Nessun risultato trovato")
            return [], "⚠️ Nessun risultato trovato."
        
        options = [{'label': f"{row['Ticker']} - {row['Descrizione']} ({row['Exchange']})", 
                    'value': f"{row['Exchange']}:{row['Ticker']}"} for _, row in filtered_df.iterrows()]
        print(f"✅ DEBUG: Generati {len(options)} opzioni per la ricerca")
        return options, ""

    @app.callback(
        [dd.Output('selected-ticker', 'value'),
         dd.Output('search-dropdown', 'value')],
        [dd.Input('search-dropdown', 'value')],
        [dd.State('selected-ticker', 'value')],
        prevent_initial_call=True
    )
    def update_selected_ticker(dropdown_value, current_value):
        # Ottieni informazioni sul trigger del callback
        ctx = dash.callback_context
        trigger = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
        print(f"🎯 DEBUG Trigger: {trigger}")
        print(f"📥 DEBUG Dropdown value ricevuto: {dropdown_value}")
        print(f"💾 DEBUG Valore corrente in selected-ticker: {current_value}")

        if dropdown_value is None:
            print("⚠️ DEBUG: Dropdown value è None")
            return current_value or "", current_value or ""
            
        if isinstance(dropdown_value, str) and dropdown_value.strip() == "":
            print("⚠️ DEBUG: Dropdown value è stringa vuota")
            return current_value or "", current_value or ""
            
        print(f"✅ DEBUG: Aggiornamento valori - dropdown: {dropdown_value}")
        return dropdown_value, dropdown_value
