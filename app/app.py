import os
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, PlainTextResponse
import logging
from pathlib import Path

app = FastAPI()

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
PORT = int(os.environ.get('PORT', 5000))
WELCOME_MESSAGE = os.environ.get('WELCOME_MESSAGE', 'Welcome to the custom app')

# Создаем директорию для логов
log_dir = Path('/app/logs')
log_dir.mkdir(parents=True, exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/logs/app.log')
    ]
)
logger = logging.getLogger(__name__)

@app.get("/", response_class=PlainTextResponse)
def welcome():
    """Эндпоинт приветствия"""
    logger.info("Welcome endpoint called")
    return WELCOME_MESSAGE

@app.get("/status")
def get_status():
    """Проверка статуса сервиса"""
    logger.info("Status endpoint called")
    return {"status": "ok"}

@app.post("/logs")
async def add_log(request: Request):
    """Добавление записи в лог"""
    # Проверка формата запроса
    if not request.headers.get('Content-Type', '').startswith('application/json'):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Request must be JSON"}
        )
    
    # Парсинг JSON
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Invalid JSON"}
        )
    
    # Запись сообщения
    message = data.get('message', '')
    logger.info(f"Received log message: {message}")
    
    with open('/app/logs/app.log', 'a') as f:
        f.write(f"{message}\n")
    
    return {"status": "logged"}

@app.get("/logs", response_class=PlainTextResponse)
def get_logs():
    """Получение логов"""
    logger.info("Logs endpoint called")
    try:
        with open('/app/logs/app.log', 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)