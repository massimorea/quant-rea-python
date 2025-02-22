from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Home QUANT-REA</h1><p>Vai su /static/rendimenti_mensile.png per vedere un grafico.</p>"

@app.route("/static/<filename>")
def serve_image(filename):
    return send_from_directory(os.path.join(app.root_path, "static"), filename)

if __name__ == "__main__":
    app.run(debug=True)

