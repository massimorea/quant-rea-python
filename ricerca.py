import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

# Carica il CSV con i ticker
df_tickers = pd.read_csv("all_ticker.csv", dtype=str)

def get_search_layout():
    """Ritorna il layout per la ricerca con input e dropdown."""
    return html.Div([
        html.Label("Digita almeno 3 caratteri per cercare un ticker:", style={'color': 'white'}),
        dcc.Input(id='search-input', type='text', value='', debounce=True, placeholder="Es. AAPL, BTC, EURUSD",
                  style={'marginLeft': '10px', 'width': '250px'}),
        dcc.Dropdown(
            id='search-dropdown',
            options=[],  # Inizialmente vuoto
            value=None,
            placeholder="Seleziona un ticker",
            clearable=True,
            style={'width': '300px', 'display': 'inline-block', 'marginLeft': '10px', 'backgroundColor': 'white', 'color': 'black'}
        ),
        html.Div(id='search-status', style={'color': 'yellow', 'marginTop': '10px'})  # Stato della ricerca
    ], style={'textAlign': 'center', 'marginBottom': '20px'})


def register_search_callbacks(app):
    """Registra il callback per aggiornare il dropdown filtrando i ticker."""
    
    @app.callback(
        [dd.Output('search-dropdown', 'options'),
         dd.Output('search-status', 'children')],
        [dd.Input('search-input', 'value')]
    )
    def update_dropdown_options(search_value):
        if not search_value or len(search_value) < 3:
            return [], "🔎 Digita almeno 3 caratteri per cercare un ticker."
        
        filtered = df_tickers[
            df_tickers['Ticker'].str.contains(search_value.upper(), na=False) |
            df_tickers['Descrizione'].str.contains(search_value.upper(), na=False)
        ]

        options = [{'label': f"{row['Ticker']} - {row['Descrizione']} ({row['Exchange']})", 'value': row['Ticker']}
                   for _, row in filtered.iterrows()]

        return options, "✅ Seleziona un asset dalla lista."

    @app.callback(
        dd.Output('search-input', 'value'),
        [dd.Input('search-dropdown', 'value')]
    )
    def update_input_with_selected_ticker(selected_ticker):
        """Quando selezioni un ticker, lo mostra nel campo di input."""
        return selected_ticker if selected_ticker else ""

