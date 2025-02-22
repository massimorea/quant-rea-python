from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route("/")
def home():
    return (
        "<h1>Home QUANT-REA</h1>"
        "<p>Per visualizzare un grafico (esempio <strong>rendimenti_mensile.png</strong>) "
        "vai su <code>/static/rendimenti_mensile.png</code>.</p>"
    )

# Se i file salvati si trovano in una sottocartella "static" del tuo progetto
@app.route("/static/<path:filename>")
def serve_image(filename):
    """
    Ritorna i file (ad esempio i grafici .png) presenti nella cartella 'static'.
    """
    return send_from_directory(
        os.path.join(app.root_path, "static"),  # Path assoluto verso la cartella 'static'
        filename
    )

if __name__ == "__main__":
    app.run(debug=True)

