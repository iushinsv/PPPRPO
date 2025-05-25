# Система
- minikube v1.36.0 on Ubuntu 24.04

- minikube запускается с --device=docker

## Развертывание кластера через команду
```sh
./deploy.sh
```
(подразумевает локальную  установку утилиты istioctl)

![delpoy_1]("pictures/deploy_1.png")
![delpoy_2]("pictures/deploy_2.png")

## ДЗ2:

**Финальные тесты для проверки работы Istio-конфигураций:**

### 1. Проверка установки Istio
```bash
# Проверим версию Istio и статус компонентов
istioctl version
kubectl -n istio-system get pods
```

![res_1]("pictures/1.png")

### 2. Проверка Gateway и базовой маршрутизации
```bash
# Получим параметры доступа
export INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}')
export INGRESS_HOST=$(minikube ip)

# Тест основных эндпоинтов
curl -v http://$INGRESS_HOST:$INGRESS_PORT/
curl -v http://$INGRESS_HOST:$INGRESS_PORT/status
```
![res_2]("pictures/2.png")

### 3. Проверка обработки неизвестных маршрутов
```bash
curl -v http://$INGRESS_HOST:$INGRESS_PORT/wrong-url
```
![res_3]("pictures/3.png")

### 4. Проверка балансировки нагрузки (LEAST_CONN)
```bash
# Запустим 10 последовательных запросов к /status
for i in {1..10}; do
  curl -s http://$INGRESS_HOST:$INGRESS_PORT/status | jq .hostname
done
```
![res_4]("pictures/4.png")



### 5. Проверка логов Istio-прокси
```bash
minikube kubectl -- logs $POD_NAME -c istio-proxy | grep -E '(timeout|retry)'
```
![res_5]("pictures/5.png")


### 6. Полная проверка системы
```bash
# Проверим все ключевые компоненты
minikube kubectl -- get gateway,virtualservice,destinationrule
minikube kubectl -- get pods -l app=custom-app
minikube kubectl -- get pods -l app=log-agent
```
![res_6.1]("pictures/6.1.png")
![res_6.2]("pictures/6.2.png")
![res_6.3]("pictures/6.3.png")

