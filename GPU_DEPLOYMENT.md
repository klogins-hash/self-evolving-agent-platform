# GPU-Enabled Cloud Deployment Guide

## Overview

This guide covers deploying the Self-Evolving Agent Platform with GPU acceleration for enhanced AI model performance and local model serving capabilities.

## Prerequisites

### Local Development
- Docker with GPU support (NVIDIA Container Toolkit)
- NVIDIA GPU with CUDA 12.1+ support
- 16GB+ GPU memory recommended

### Cloud Deployment
- Cloud account with GPU instance access
- Docker registry (Docker Hub, AWS ECR, GCP Container Registry)
- GPU-enabled compute instances

## Local GPU Setup

### 1. Install NVIDIA Container Toolkit

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### 2. Test GPU Access

```bash
# Test NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:12.1-base-ubuntu22.04 nvidia-smi
```

### 3. Deploy with GPU Support

```bash
# Build and run GPU-enabled containers
docker-compose -f docker-compose.gpu.yml up --build -d

# Or use Make command
make gpu-deploy
```

## Cloud Provider Setup

### AWS (ECS with GPU)

#### 1. Create GPU-enabled ECS Cluster

```bash
# Create cluster with GPU instances
aws ecs create-cluster --cluster-name agent-platform-gpu

# Launch GPU instances (g4dn.xlarge recommended)
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type g4dn.xlarge \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxx \
  --subnet-id subnet-xxxxxxxx \
  --user-data file://ecs-gpu-userdata.sh
```

#### 2. Deploy Task Definition

```bash
# Register GPU task definition
aws ecs register-task-definition --cli-input-json file://cloud/aws-gpu-task.json

# Create service
aws ecs create-service \
  --cluster agent-platform-gpu \
  --service-name agent-platform-service \
  --task-definition self-evolving-agent-platform-gpu:1 \
  --desired-count 1
```

### Google Cloud Platform (GKE with GPU)

#### 1. Create GKE Cluster with GPU Nodes

```bash
# Create cluster
gcloud container clusters create agent-platform-gpu \
  --accelerator type=nvidia-tesla-t4,count=1 \
  --machine-type n1-standard-4 \
  --num-nodes 1 \
  --zone us-central1-a

# Install NVIDIA drivers
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded.yaml
```

#### 2. Deploy to GKE

```bash
# Apply Kubernetes manifests
kubectl apply -f cloud/gke-gpu-deployment.yml
kubectl apply -f cloud/gke-service.yml
```

### Azure (ACI with GPU)

#### 1. Create GPU Container Instance

```bash
# Deploy with Azure CLI
az container create \
  --resource-group agent-platform-rg \
  --name agent-platform-gpu \
  --image your-registry/agent-platform-backend-gpu:latest \
  --gpu-count 1 \
  --gpu-sku V100 \
  --cpu 4 \
  --memory 16 \
  --ports 8000 8001
```

## Docker Registry Setup

### 1. Build and Push GPU Images

```bash
# Build GPU-enabled backend
docker build -f backend/Dockerfile.gpu -t your-registry/agent-platform-backend-gpu:latest ./backend

# Build standard frontend
docker build -f frontend/Dockerfile -t your-registry/agent-platform-frontend:latest ./frontend

# Push to registry
docker push your-registry/agent-platform-backend-gpu:latest
docker push your-registry/agent-platform-frontend:latest
```

### 2. Automated CI/CD with GitHub Actions

```yaml
# .github/workflows/gpu-deploy.yml
name: GPU Docker Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Login to Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ secrets.DOCKER_REGISTRY }}
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
          
      - name: Build and push GPU backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          file: ./backend/Dockerfile.gpu
          push: true
          tags: ${{ secrets.DOCKER_REGISTRY }}/agent-platform-backend-gpu:latest
```

## Performance Optimization

### GPU Memory Management

```python
# backend/app/core/gpu_config.py
import torch
import os

class GPUConfig:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.gpu_memory_fraction = float(os.getenv("GPU_MEMORY_FRACTION", "0.8"))
        
    def configure_memory(self):
        if torch.cuda.is_available():
            torch.cuda.set_per_process_memory_fraction(self.gpu_memory_fraction)
            torch.cuda.empty_cache()
```

### Model Caching Strategy

```python
# backend/app/models/gpu_models.py
from transformers import AutoModel, AutoTokenizer
import torch

class GPUModelManager:
    def __init__(self):
        self.models = {}
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def load_model(self, model_name: str):
        if model_name not in self.models:
            model = AutoModel.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            model.to(self.device)
            model.eval()
            
            self.models[model_name] = {
                "model": model,
                "tokenizer": tokenizer
            }
        
        return self.models[model_name]
```

## Monitoring and Scaling

### GPU Metrics Collection

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  nvidia-exporter:
    image: mindprince/nvidia_gpu_prometheus_exporter:0.1
    ports:
      - "9445:9445"
    volumes:
      - /usr/lib/x86_64-linux-gnu/libnvidia-ml.so:/usr/lib/x86_64-linux-gnu/libnvidia-ml.so
      - /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1:/usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
```

### Auto-scaling Configuration

```yaml
# Kubernetes HPA for GPU workloads
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agent-platform-gpu-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agent-platform-gpu
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: nvidia.com/gpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Cost Optimization

### Spot Instances
- Use spot instances for development/testing
- Implement graceful shutdown handling
- Consider preemptible instances on GCP

### GPU Sharing
- Use NVIDIA MPS for multi-process sharing
- Implement model batching for efficiency
- Consider fractional GPU allocation

### Scheduled Scaling
```bash
# Scale down during off-hours
0 18 * * * kubectl scale deployment agent-platform-gpu --replicas=0
0 8 * * * kubectl scale deployment agent-platform-gpu --replicas=2
```

## Troubleshooting

### Common Issues

1. **GPU Not Detected**
   ```bash
   # Check NVIDIA drivers
   nvidia-smi
   
   # Verify Docker GPU support
   docker run --rm --gpus all nvidia/cuda:12.1-base-ubuntu22.04 nvidia-smi
   ```

2. **Out of Memory Errors**
   ```python
   # Reduce batch size or model size
   export GPU_MEMORY_FRACTION=0.6
   export BATCH_SIZE=2
   ```

3. **CUDA Version Mismatch**
   ```bash
   # Check CUDA compatibility
   nvcc --version
   python -c "import torch; print(torch.version.cuda)"
   ```

## Security Considerations

- Use private registries for GPU images
- Implement resource quotas and limits
- Monitor GPU usage and costs
- Secure API keys in cloud secret managers
- Enable audit logging for GPU resource access

## Next Steps

1. Deploy basic GPU setup locally
2. Test with cloud provider of choice
3. Implement monitoring and alerting
4. Set up CI/CD pipeline for automated deployments
5. Optimize for cost and performance based on usage patterns

This setup provides a robust foundation for GPU-accelerated AI agent operations with cloud scalability.
