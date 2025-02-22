import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Scarica i dati storici di Bitcoin
btc_data = yf.download('BTC-USD')

# Calcola i rendimenti giornalieri
btc_data['Rendimento_Giornaliero'] = btc_data['Close'].pct_change()

# Calcola i rendimenti settimanali e mensili
btc_data['Rendimento_Settimanale'] = btc_data['Close'].resample('W').ffill().pct_change()
btc_data['Rendimento_Mensile'] = btc_data['Close'].resample('M').ffill().pct_change()

# Calcola la volatilità giornaliera (deviazione standard dei rendimenti) su una finestra di 30 giorni
btc_data['Volatilità_Giornaliera'] = btc_data['Rendimento_Giornaliero'].rolling(window=30).std() * np.sqrt(365)

# Funzione per plottare i rendimenti anno per anno
def plot_rendimenti_per_frequenza(rendimento, titolo):
    rendimento_annualizzato = rendimento.groupby(rendimento.index.year).mean() * 100
    plt.figure(figsize=(10, 6))
    plt.bar(rendimento_annualizzato.index, rendimento_annualizzato, color='blue', alpha=0.7)
    plt.title(f'Rendimento {titolo} Annualizzato di Bitcoin (BTC-USD)')
    plt.xlabel('Anno')
    plt.ylabel(f'Rendimento {titolo} (%)')
    plt.grid(True)
    plt.show()

# Funzione per plottare la volatilità
def plot_volatilita():
    plt.figure(figsize=(10, 6))
    plt.plot(btc_data.index, btc_data['Volatilità_Giornaliera'], label='Volatilità Annualizzata', color='orange')
    plt.title('Volatilità Annualizzata di Bitcoin (BTC-USD)')
    plt.xlabel('Data')
    plt.ylabel('Volatilità')
    plt.grid(True)
    plt.legend()
    plt.show()

# Plot dei rendimenti giornalieri annualizzati
plot_rendimenti_per_frequenza(btc_data['Rendimento_Giornaliero'], 'Giornaliero')

# Plot dei rendimenti settimanali annualizzati
plot_rendimenti_per_frequenza(btc_data['Rendimento_Settimanale'], 'Settimanale')

# Plot dei rendimenti mensili annualizzati
plot_rendimenti_per_frequenza(btc_data['Rendimento_Mensile'], 'Mensile')

# Plot della volatilità annualizzata
plot_volatilita()
