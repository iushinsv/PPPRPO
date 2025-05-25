from flask import Flask, request, jsonify
import os
import logging
from datetime import datetime
import time

app = Flask(__name__)

# Configuration from environment variables
welcome_message = os.environ.get('WELCOME_MSG', 'Welcome to the custom app')
log_level = os.environ.get('LOG_LEVEL', 'INFO')
port = int(os.environ.get('PORT', 5000))

# Configure application logging
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler()
    ]
)

# Ensure logs directory exists
logs_dir = '/app/logs'
os.makedirs(logs_dir, exist_ok=True)

@app.route('/')
def home():
    return welcome_message

@app.route('/status')
def status():
    import socket
    return jsonify({
        "status": "ok", 
        "hostname": socket.gethostname()
    })

@app.route('/log', methods=['POST'])
def log_message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid data"}), 400
    
    try:
        time.sleep(3)  # Имитация долгой обработки
        logging.info(data['message'])
        return jsonify({"status": "logged"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logs')
def get_logs():
    try:
        with open('/app/logs/app.log', 'r') as f:
            logs = f.read()
        return logs.replace('\n', '<br>')  # Сохраняем форматирование для браузера
    except FileNotFoundError:
        return jsonify({"error": "Logs not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)