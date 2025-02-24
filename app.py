from flask import Flask, request, jsonify
import redis
from rq import Queue
import os

# Inizializzazione Flask app
app = Flask(__name__)

# Configurazione Redis
# Usa URL di Redis da variabile ambiente o default locale
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_conn = redis.from_url(REDIS_URL)

# Creazione code per i diversi worker
asset_queue = Queue('asset', connection=redis_conn)
volatilita_queue = Queue('volatilita', connection=redis_conn)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "endpoints": {
            "/asset": "Analisi asset",
            "/volatilita": "Analisi volatilità"
        }
    })

@app.route('/asset', methods=['POST'])
def process_asset():
    try:
        data = request.get_json()
        if not data or 'ticker' not in data:
            return jsonify({"error": "Ticker non specificato"}), 400
        
        # Invia il job alla coda asset
        job = asset_queue.enqueue('rendimenti_asset.py', data['ticker'])
        
        return jsonify({
            "status": "success",
            "job_id": job.id,
            "message": f"Analisi asset avviata per {data['ticker']}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/volatilita', methods=['POST'])
def process_volatilita():
    try:
        data = request.get_json()
        if not data or 'ticker' not in data:
            return jsonify({"error": "Ticker non specificato"}), 400
        
        # Invia il job alla coda volatilità
        job = volatilita_queue.enqueue('rendimenti_volatilita.py', data['ticker'])
        
        return jsonify({
            "status": "success",
            "job_id": job.id,
            "message": f"Analisi volatilità avviata per {data['ticker']}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status/<job_id>')
def get_job_status(job_id):
    try:
        # Cerca il job in entrambe le code
        job_asset = asset_queue.fetch_job(job_id)
        job_vol = volatilita_queue.fetch_job(job_id)
        
        job = job_asset or job_vol
        
        if not job:
            return jsonify({"error": "Job non trovato"}), 404
            
        status = {
            "job_id": job.id,
            "status": job.get_status(),
            "result": job.result if job.is_finished else None,
            "error": str(job.exc_info) if job.is_failed else None
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
