#!/bin/bash
set -eo pipefail

# Initialize Minikube and install Istio
echo "Starting Minikube and setting up Istio..."
minikube start --driver=docker
eval $(minikube docker-env)

# Install Istio
ISTIO_VERSION=1.18.0
echo "Downloading Istio ${ISTIO_VERSION}..."
curl -sL https://github.com/istio/istio/releases/download/${ISTIO_VERSION}/istio-${ISTIO_VERSION}-linux-amd64.tar.gz | tar xz
export PATH="${PWD}/istio-${ISTIO_VERSION}/bin:$PATH"
istioctl install --set profile=demo -y
minikube kubectl -- label namespace default istio-injection=enabled

# Build app image
echo "Building Docker image..."
docker build -t custom-app . || { echo "Docker build failed"; exit 1; }

# Create host directories
minikube ssh "sudo mkdir -p /var/log/app /var/log/app-archives && sudo chmod 777 /var/log/app /var/log/app-archives"

# Apply Kubernetes manifests
declare -a manifests=(
    "k8s/configmap.yaml"
    "k8s/deployment.yaml"
    "k8s/service.yaml"
    "k8s/daemonset.yaml"
    "k8s/cronjob.yaml"
    "k8s/istio-gateway.yaml"
    "k8s/istio-virtualservice.yaml"
    "k8s/destination-rule.yaml"
)

echo "Applying manifests..."
for manifest in "${manifests[@]}"; do
    if [ ! -f "$manifest" ]; then
        echo "Error: Missing $manifest"
        exit 1
    fi
    minikube kubectl -- apply -f "$manifest"
done

# Wait for components
echo "Waiting for deployment rollout..."
minikube kubectl -- rollout status deployment/custom-app --timeout=180s

echo "Checking DaemonSet..."
minikube kubectl -- rollout status daemonset/log-agent --timeout=120s

echo -e "\nDeployment complete!"
echo -e "Access endpoints through Istio Gateway:"
echo -e "export INGRESS_PORT=\$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name==\"http2\")].nodePort}')"
echo -e "export INGRESS_HOST=\$(minikube ip)"
echo -e "curl http://\$INGRESS_HOST:\$INGRESS_PORT"
echo -e "\nView agent logs with:"
echo -e "kubectl logs -l app=log-agent"
echo -e "\nView archives in Minikube:"
echo -e "minikube ssh 'ls -lh /var/log/app-archives'"