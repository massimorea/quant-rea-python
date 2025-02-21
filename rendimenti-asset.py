# Clonare il repository tvdatafeed
!git clone https://github.com/rongardF/tvdatafeed.git

# Spostarsi nella directory e installare la libreria
%cd tvdatafeed
!pip install .


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import zscore
from tvDatafeed import TvDatafeed, Interval

tv = TvDatafeed()


# Scarica i dati dello S&P 500 da TradingView
ticker = "SPX"  # Ticker per S&P 500 su TradingView
data = tv.get_hist(ticker, exchange="", interval=Interval.in_daily, n_bars=50000)  # Corretto Interval.in_1d

# Controlla se i dati sono stati scaricati correttamente
if data is None or data.empty:
    raise ValueError("Errore nel recupero dei dati da TradingView. Verifica l'autenticazione o il ticker.")

# Converti l'indice in formato datetime
data.index = pd.to_datetime(data.index)
data = data.sort_index()

# Calcola i rendimenti annuali
data['Year'] = data.index.year  # Aggiungi una colonna con l'anno
annual_data = data.groupby('Year')['close'].last().pct_change().dropna()  # Rendimenti annuali

# Converti annual_data in una Series 1D
annual_data = annual_data.squeeze()  # Rimuove dimensioni extra

# Calcola il rendimento annualizzato medio
annualized_return = annual_data.mean()

# Calcola la deviazione standard annualizzata
annualized_std = annual_data.std()

# Calcola lo z-score dei rendimenti annuali
annual_data_zscore = zscore(annual_data)

# Creazione di un DataFrame per i risultati
results = pd.DataFrame({
    'Year': annual_data.index,
    'Annual Return': annual_data.values,  # Usa .values per ottenere un array 1D
    'Z-Score': annual_data_zscore
})

# Plot dei rendimenti annuali e dello z-score
plt.figure(figsize=(14, 7))

# Plot dei rendimenti annuali
plt.subplot(2, 1, 1)
plt.bar(results['Year'], results['Annual Return'], color='blue', alpha=0.7, label='Rendimenti Annuali')
plt.axhline(annualized_return, color='red', linestyle='--', label='Rendimento Annualizzato Medio')
plt.axhline(annualized_return + annualized_std, color='green', linestyle='--', label='Deviazione Standard (±1)')
plt.axhline(annualized_return - annualized_std, color='green', linestyle='--')
plt.title('Rendimenti Annuali dello S&P 500')
plt.xlabel('Anno')
plt.ylabel('Rendimento Annuale')
plt.legend()

# Plot dello z-score
plt.subplot(2, 1, 2)
plt.plot(results['Year'], results['Z-Score'], color='orange', label='Z-Score dei Rendimenti Annuali')
plt.axhline(0, color='black', linestyle='--', label='Media (Z = 0)')
plt.axhline(1, color='gray', linestyle='--', label='Z = ±1')
plt.axhline(-1, color='gray', linestyle='--')
plt.title('Z-Score dei Rendimenti Annuali')
plt.xlabel('Anno')
plt.ylabel('Z-Score')
plt.legend()

plt.tight_layout()
plt.show()

# Stampa dei risultati
print(f"Rendimento Annualizzato Medio: {annualized_return:.4f}")
print(f"Deviazione Standard Annualizzata: {annualized_std:.4f}")
print("\nTabella dei Rendimenti Annuali e Z-Score:")
print(results)

