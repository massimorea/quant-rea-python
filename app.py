from flask import Flask
import rendimenti-asset  # Se vuoi richiamare funzioni dal tuo script
#import rendimenti_v  # Se vuoi richiamare funzioni dal tuo script

app = Flask(__name__)

@app.route("/")
def home():
    # Esegui qualche funzione definita in rendimenti-asset.py
    # result = rendimenti_asset.calcola_qualcosa()
    return "<h1>Home QUANT-REA</h1>"

if __name__ == "__main__":
    app.run(debug=True)
