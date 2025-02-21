# app.py
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>QUANT-REA</h1><p>Ecco il nostro endpoint web su Heroku!</p>"

if __name__ == "__main__":
    app.run(debug=True)
