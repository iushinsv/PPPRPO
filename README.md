# Sber Kubernetes Deployment 

Микросервисная система для работы с логами и метриками

![Архитектура](./imgs/deployment-diagram.png)

## Быстрый старт

### Установка зависимостей
```bash
pip install -r requirements.txt

# Основное приложение (порт 5000)
uvicorn app:app --host 0.0.0.0 --port 5000

# Сервис журналирования (порт 5001)
uvicorn server:app --host 0.0.0.0 --port 5001

# Проброс портов основного приложения
kubectl port-forward service/app-service 5000:80

# Доступ к метрикам приложения
curl http://localhost:5000/metrics

kubectl port-forward -n journal-system svc/prometheus 5050:5050