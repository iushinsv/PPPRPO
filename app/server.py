import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import PlainTextResponse
from pathlib import Path

app = FastAPI()

LOG_SEVERITY = os.environ.get('LOG_SEVERITY', 'INFO')
SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5000))
GREETING = os.environ.get('GREETING', 'Welcome to the custom app')

# Создаем директорию для логов
log_dir = Path('/application/journal')
log_dir.mkdir(parents=True, exist_ok=True)

# Настройка системы логирования
logging.basicConfig(
    level=getattr(logging, LOG_SEVERITY),
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/application/journal/app.log')
    ]
)
journal = logging.getLogger('journal_service')

@app.get("/", response_class=PlainTextResponse)
async def root():
    """Корневой эндпоинт"""
    journal.info("Запрос к корневому маршруту")
    return GREETING

@app.get("/status")
async def health_check():
    """Проверка состояния сервиса"""
    journal.info("Проверка работоспособности")
    return {"status": "ok"}

@app.post("/log")
async def add_log_entry(data: dict):
    """Добавление записи в журнал"""
    if 'message' not in data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отсутствует поле 'message' в запросе"
        )
    
    entry = data['message']
    journal.info(f"Получена запись: {entry}")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {entry}"
    
    try:
        with open('/application/journal/app.log', 'a') as log_file:
            log_file.write(f"{log_entry}\n")
    except IOError as e:
        journal.error(f"Ошибка записи в журнал: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка записи в журнал"
        )
    
    return {
        "result": "запись добавлена",
        "time": timestamp
    }

@app.get("/logs", response_class=PlainTextResponse)
async def view_journal():
    """Получение полного содержимого журнала"""
    journal.info("Запрос содержимого журнала")
    try:
        with open('/application/journal/app.log', 'r') as log_file:
            return log_file.read()
    except Exception as e:
        journal.error(f"Ошибка чтения журнала: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=SERVICE_PORT
    )