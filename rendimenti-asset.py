import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import zscore
from tvDatafeed import TvDatafeed, Interval

def main():
    tv = TvDatafeed()  # Se serve username/password, passali: TvDatafeed(username='...', password='...')
    
    # Scarica i dati dello S&P 500 da TradingView
    ticker = "SPX"  
    data = tv.get_hist(
        symbol=ticker,
        exchange="",
        interval=Interval.in_daily,
        n_bars=50000
    )
    
    if data is None or data.empty:
        raise ValueError("Errore nel recupero dei dati da TradingView. Verifica l'autenticazione o il ticker.")
    
    # Converti l'indice in datetime e sort
    data.index = pd.to_datetime(data.index)
    data = data.sort_index()
    
    # Rendimenti annuali
    data['Year'] = data.index.year
    annual_data = data.groupby('Year')['close'].last().pct_change().dropna()
    annual_data = annual_data.squeeze()  # in caso di dimensioni extra
    
    annualized_return = annual_data.mean()
    annualized_std = annual_data.std()
    annual_data_zscore = zscore(annual_data)
    
    results = pd.DataFrame({
        'Year': annual_data.index,
        'Annual Return': annual_data.values,
        'Z-Score': annual_data_zscore
    })
    
    # Plot
    plt.figure(figsize=(14, 7))
    
    # Rendimenti
    plt.subplot(2, 1, 1)
    plt.bar(results['Year'], results['Annual Return'], color='blue', alpha=0.7, label='Rendimenti Annuali')
    plt.axhline(annualized_return, color='red', linestyle='--', label='Rendimento Annualizzato Medio')
    plt.axhline(annualized_return + annualized_std, color='green', linestyle='--', label='Deviazione Standard (±1)')
    plt.axhline(annualized_return - annualized_std, color='green', linestyle='--')
    plt.title('Rendimenti Annuali dello S&P 500')
    plt.xlabel('Anno')
    plt.ylabel('Rendimento Annuale')
    plt.legend()
    
    # Z-Score
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
    
    print(f"Rendimento Annualizzato Medio: {annualized_return:.4f}")
    print(f"Deviazione Standard Annualizzata: {annualized_std:.4f}")
    print("\nTabella dei Rendimenti Annuali e Z-Score:")
    print(results)

if __name__ == "__main__":
    main()
