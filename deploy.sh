#!/bin/bash

export DOCKER_HOST=unix:///var/run/docker.sock

istioctl install --set profile=demo -y
docker build -t custom-app:latest .
minikube image load custom-app:latest
kubectl label namespace journal istio-injection=enabled --overwrite
kubectl apply -f kub/prometheus.yaml
kubectl apply -f kub/configmap.yml
kubectl apply -f kub/pod.yml
kubectl wait --for=condition=Ready pod/app-pod --timeout=60s
kubectl exec app-pod -- curl -s http://localhost:5000/status
kubectl apply -f kub/deployment.yml
kubectl wait --for=condition=Available deployment/app-deployment --timeout=60s
kubectl apply -f kub/service.yml
kubectl apply -f kub/pv.yml
kubectl apply -f kub/pvc.yml
kubectl apply -f kub/daemonset.yml
kubectl apply -f kub/cronjob.yml
kubectl apply -f kub/istio-gw.yaml
kubectl apply -f kub/istio-vs.yaml
kubectl apply -f kub/istio-dest.yaml
kubectl wait --namespace=journal --for=condition=Available deployment/prometheus --timeout=60s