import os
import logging
from datetime import datetime
from fastapi import FastAPI, Request, Response, status, BackgroundTasks

app = FastAPI()

LOG_SEVERITY = os.environ.get('LOG_SEVERITY', 'INFO')
SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5000))
GREETING = os.environ.get('GREETING', 'Welcome to the custom app')

logging.basicConfig(
    level=getattr(logging, LOG_SEVERITY),
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/application/journal/app.log')
    ]
)
journal = logging.getLogger('journal_service')

@app.get("/")
async def home():
    journal.info("Запрос к корневому маршруту")
    return GREETING

@app.get("/status")
async def health_check():
    journal.info("Проверка работоспособности")
    return {"status": "ok"}

@app.post("/log")
async def journal_entry(data: dict, background_tasks: BackgroundTasks):
    entry = data.get('message', '')
    journal.info(f"Получена запись: {entry}")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    background_tasks.add_task(
        lambda: write_journal_entry(entry, timestamp)
    
    return {"result": "запись добавлена", "time": timestamp}

def write_journal_entry(entry: str, timestamp: str):
    with open('/application/journal/app.log', 'a') as journal_file:
        journal_file.write(f"[{timestamp}] {entry}\n")

@app.get("/logs")
async def view_journal():
    journal.info("Запрос содержимого журнала")
    try:
        with open('/application/journal/app.log', 'r') as journal_file:
            content = journal_file.read()
        return Response(content=content, media_type="text/plain")
    except Exception as e:
        journal.error(f"Ошибка чтения журнала: {e}")
        return {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)