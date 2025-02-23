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
            options=[],  # Verrà aggiornato dinamicamente
            value=None,  # Il valore selezionato rimane
            placeholder="Digita almeno 3 caratteri per cercare...",
            clearable=False,
            searchable=True,
            style={'width': '400px', 'color': 'black', 'backgroundColor': 'white'}
        ),
        html.Div(id='search-status', style={'color': 'yellow', 'marginTop': '5px', 'textAlign': 'center'}),

        # ✅ Mantiene il ticker selezionato
        dcc.Input(id='selected-ticker', type='text', value="", style={'display': 'online'})
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
         dd.Output('search-dropdown', 'value')],  # ✅ Mantiene il valore nel dropdown
        [dd.Input('search-dropdown', 'value')],
        [dd.State('selected-ticker', 'value')]
    )
    def update_selected_ticker(value, current_ticker):
        return value or current_ticker, value or current_ticker  # ✅ Evita il reset

