import os
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from flask import Flask
import threading

app = Flask(__name__)

def plot_rendimenti_per_frequenza(rendimento, frequenza, filename):
    rendimento_annualizzato = rendimento.groupby(rendimento.index.year).mean() * 100
    plt.figure(figsize=(10, 6))
    plt.bar(rendimento_annualizzato.index, rendimento_annualizzato, color='blue', alpha=0.7)
    plt.title(f"Rendimenti {frequenza} Annualizzati di BTC-USD")
    plt.xlabel('Anno')
    plt.ylabel(f'Rendimento {frequenza} (%)')
    plt.grid(True)
    os.makedirs("static", exist_ok=True)
    filepath = os.path.join("static", filename)
    plt.savefig(filepath)
    plt.close()

def plot_volatilita(df, filename):
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['Volatilità_Giornaliera'], color='orange', label='Volatilità Annualizzata')
    plt.title('Volatilità Annualizzata di Bitcoin (BTC-USD)')
    plt.xlabel('Data')
    plt.ylabel('Volatilità')
    plt.grid(True)
    plt.legend()
    os.makedirs("static", exist_ok=True)
    filepath = os.path.join("static", filename)
    plt.savefig(filepath)
    plt.close()

def main():
    btc_data = yf.download('BTC-USD')
    btc_data['Rendimento_Giornaliero'] = btc_data['Close'].pct_change()
    btc_data['Rendimento_Settimanale'] = btc_data['Close'].resample('W').ffill().pct_change()
    btc_data['Rendimento_Mensile'] = btc_data['Close'].resample('ME').ffill().pct_change()
    btc_data['Volatilità_Giornaliera'] = btc_data['Rendimento_Giornaliero'].rolling(window=30).std() * np.sqrt(365)
    plot_rendimenti_per_frequenza(btc_data['Rendimento_Giornaliero'], 'Giornaliero', 'rendimenti_giornaliero.png')
    plot_rendimenti_per_frequenza(btc_data['Rendimento_Settimanale'], 'Settimanale', 'rendimenti_settimanale.png')
    plot_rendimenti_per_frequenza(btc_data['Rendimento_Mensile'], 'Mensile', 'rendimenti_mensile.png')
    plot_volatilita(btc_data, 'volatilita.png')
    print("Analisi volatilità Bitcoin completata. Grafici salvati in static/")

@app.route("/calcola_volatilita")
def run_analysis():
    thread = threading.Thread(target=main)
    thread.start()
    return "Analisi della volatilità avviata!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
