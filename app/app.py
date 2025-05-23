import os
import logging
from time import time
from fastapi import FastAPI, Request, Response, status, BackgroundTasks
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
PORT = int(os.environ.get('PORT', 5000))
WELCOME_MESSAGE = os.environ.get('WELCOME_MESSAGE', 'Welcome to the custom app')

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/logs/app.log')
    ]
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'flask_app_requests_total', 
    'Total App HTTP Requests', 
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'flask_app_request_latency_seconds',
    'Flask Request latency',
    ['endpoint']
)

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time()
    method = request.method
    endpoint = request.url.path
    try:
        response = await call_next(request)
    except Exception as e:
        response = Response(str(e), status_code=500)
    latency = time() - start_time
    
    REQUEST_COUNT.labels(method, endpoint, response.status_code).inc()
    REQUEST_LATENCY.labels(endpoint).observe(latency)
    return response

@app.get("/")
async def welcome():
    logger.info("Welcome endpoint called")
    return WELCOME_MESSAGE

@app.get("/status")
async def get_status():
    logger.info("Status endpoint called")
    return {"status": "ok"}

@app.post("/log")
async def log_message(data: dict, background_tasks: BackgroundTasks):
    message = data.get('message', '')
    logger.info(f"Received log message: {message}")
    
    background_tasks.add_task(
        lambda: write_log_message(message)
    )
    return {"status": "logged"}

def write_log_message(message: str):
    with open('/app/logs/app.log', 'a') as f:
        f.write(f"{message}\n")

@app.get("/logs")
async def get_logs():
    logger.info("Logs endpoint called")
    try:
        with open('/app/logs/app.log', 'r') as f:
            logs = f.read()
        return Response(content=logs, media_type="text/plain")
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)