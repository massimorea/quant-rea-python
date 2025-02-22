import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Scarica i dati storici di Bitcoin
btc_data = yf.download('BTC-USD')

# Calcola i rendimenti giornalieri
btc_data['Rendimento_Giornaliero'] = btc_data['Close'].pct_change()

# Calcola i rendimenti settimanali e mensili
btc_data['Rendimento_Settimanale'] = (btc_data['Close']
                                      .resample('W').ffill()
                                      .pct_change())

btc_data['Rendimento_Mensile'] = (btc_data['Close']
                                  .resample('M').ffill()
                                  .pct_change())

# Calcola la volatilità giornaliera (deviazione standard dei rendimenti) su finestra di 30 giorni
btc_data['Volatilità_Giornaliera'] = (btc_data['Rendimento_Giornaliero']
                                      .rolling(window=30).std()
                                      * np.sqrt(365))

def plot_rendimenti_per_frequenza(rendimento, frequenza, filename):
    """
    Calcola il rendimento medio (in %) per anno, e salva un grafico a barre su file.
    rendimento: Series di rendimenti
    frequenza: stringa ('Giornaliero', 'Settimanale', 'Mensile')
    filename: nome del file PNG da salvare
    """
    rendimento_annualizzato = rendimento.groupby(rendimento.index.year).mean() * 100

    plt.figure(figsize=(10, 6))
    plt.bar(rendimento_annualizzato.index, rendimento_annualizzato,
            color='blue', alpha=0.7)
    plt.title(f"Rendimenti {frequenza} Annualizzati di BTC-USD")
    plt.xlabel('Anno')
    plt.ylabel(f'Rendimento {frequenza} (%)')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_volatilita(df, filename):
    """
    Plot della volatilità annualizzata salvata nella colonna 'Volatilità_Giornaliera'.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['Volatilità_Giornaliera'],
             color='orange', label='Volatilità Annualizzata')
    plt.title('Volatilità Annualizzata di Bitcoin (BTC-USD)')
    plt.xlabel('Data')
    plt.ylabel('Volatilità')
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def main():
    # Plot dei rendimenti giornalieri annualizzati
    plot_rendimenti_per_frequenza(
        btc_data['Rendimento_Giornaliero'],
        'Giornaliero',
        'rendimenti_giornaliero.png'
    )

    # Plot dei rendimenti settimanali annualizzati
    plot_rendimenti_per_frequenza(
        btc_data['Rendimento_Settimanale'],
        'Settimanale',
        'rendimenti_settimanale.png'
    )

    # Plot dei rendimenti mensili annualizzati
    plot_rendimenti_per_frequenza(
        btc_data['Rendimento_Mensile'],
        'Mensile',
        'rendimenti_mensile.png'
    )

    # Plot della volatilità annualizzata
    plot_volatilita(btc_data, 'volatilita.png')

    # Stampa qualche info in console/log
    print("Analisi volatilità Bitcoin completata. Grafici salvati in:")
    print("  - rendimenti_giornaliero.png")
    print("  - rendimenti_settimanale.png")
    print("  - rendimenti_mensile.png")
    print("  - volatilita.png")

if __name__ == "__main__":
    main()
