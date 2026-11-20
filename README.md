# Self-Healing FastAPI Service on Amazon EKS

## Project Overview

This repository contains my end-to-end Kubernetes deployment on Amazon EKS (`us-east-1`).

I built a production-style DevOps project covering persistent gp3 storage, Horizontal Pod Autoscaling (HPA), Prometheus and Grafana monitoring, a custom Python self-healing controller (`healer.py`), automated GitHub Actions CI/CD, and AWS cost control.

I developed a Python FastAPI service (`app/main.py`) exposing `/healthz`, `/ready`, and `/metrics`, containerized it with Docker, and deployed it into the `production-app` namespace on the EKS cluster `devops-selfhealing-cluster`.

## AWS Infrastructure

- AWS Region: `us-east-1`
- EKS Cluster: `devops-selfhealing-cluster`
- Namespace: `production-app`
- Persistent Storage: AWS EBS gp3
- PVC Size: `5Gi`

## Application Endpoints

| Endpoint | Purpose |
|---|---|
| `/healthz` | Application liveness check |
| `/ready` | Application readiness check |
| `/metrics` | Prometheus metrics endpoint |

## Kubernetes Deployment

The application is deployed using Kubernetes YAML manifests.

Features include:

- Kubernetes Deployment with multiple replicas
- Liveness and readiness probes
- ClusterIP Service
- ConfigMap for non-sensitive configuration
- Kubernetes Secret for sensitive configuration
- Persistent Volume Claim
- Kubernetes RBAC for the healer

## Persistent Storage

Configured a `5Gi` AWS EBS `gp3` PersistentVolumeClaim to provide persistent block storage through the AWS EBS CSI driver.

## Horizontal Pod Autoscaling

Configured Kubernetes HPA with:

- Minimum replicas: 2
- Maximum replicas: 5
- Target CPU utilization: 70%

HPA automatically adjusts the application replica count based on CPU utilization.

## Monitoring and Observability

### Prometheus

- Collects application metrics.
- Uses ServiceMonitor to discover the FastAPI Kubernetes Service.
- Scrapes the `/metrics` endpoint.

### Grafana

- Visualizes application metrics through dashboards.
- Uses ConfigMap-based dashboard provisioning.

### Metrics Server

Provides CPU and memory resource metrics to Kubernetes and supports HPA functionality.

## Custom Python Self-Healing Controller

Developed `healer/healer.py`, a custom Python-based Kubernetes pod health watcher.

### Problem

Standard Kubernetes liveness probes restart unhealthy containers inside their existing pods. However, repeated failures and certain pod-level problems may require additional remediation.

### Solution

The custom healer:

1. Watches pods in the `production-app` namespace.
2. Inspects container waiting reasons.
3. Checks container restart counts.
4. Uses `MAX_RESTARTS_THRESHOLD=5`.
5. Identifies configured unhealthy pod conditions.
6. Deletes eligible broken pods through the Kubernetes API.
7. Allows the ReplicaSet to create replacement pods.

### Safety and Testing

- Uses a dedicated Kubernetes ServiceAccount.
- Uses scoped RBAC permissions.
- Performs dry-run checks before remediation.
- Tested detection using a simulated failing pod named `healer-sim-crash`.
- Avoids intentionally targeting healthy production replicas during testing.

## CI/CD Pipeline

Implemented GitHub Actions automation using:

`.github/workflows/ci-cd.yaml`

The workflow automates the application build, Docker image creation, and deployment to Amazon EKS when changes are pushed to the `main` branch.

## Project Structure

```text
project3-eks-selfhealing/
├── .github/
│   └── workflows/
│       └── ci-cd.yaml
├── app/
│   └── main.py
├── healer/
│   └── healer.py
├── k8s/
│   ├── 00-namespace.yaml
│   ├── 01-configmap.yaml
│   ├── 02-secret.yaml
│   ├── 03-pvc.yaml
│   ├── 04-deployment.yaml
│   ├── 05-service.yaml
│   ├── 06-hpa.yaml
│   └── 07-rbac.yaml
├── monitoring/
│   ├── servicemonitor.yaml
│   └── grafana-dashboard-cm.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Technologies Used

| Category | Technologies |
|---|---|
| Cloud | AWS |
| Containerization | Docker |
| Orchestration | Kubernetes, Amazon EKS |
| Application | Python, FastAPI |
| Storage | AWS EBS gp3 |
| Autoscaling | Kubernetes HPA |
| Monitoring | Prometheus, Grafana |
| Resource Metrics | Metrics Server |
| Automation | Python, Kubernetes API |
| Security | Kubernetes RBAC |
| CI/CD | GitHub Actions |
| Configuration | YAML |

## Key Learnings

- Deploying containerized applications on Amazon EKS.
- Managing Kubernetes Deployments, Services, and Pods.
- Configuring persistent storage using AWS EBS.
- Implementing automatic scaling using HPA.
- Monitoring metrics using Prometheus and Grafana.
- Understanding Kubernetes probes and pod failure scenarios.
- Developing a custom Python self-healing controller.
- Configuring Kubernetes ServiceAccounts and RBAC.
- Automating CI/CD workflows using GitHub Actions.
- Understanding AWS resource management and cost optimization.

## Project Goal

The goal of this project is to demonstrate practical DevOps and Kubernetes skills by building a monitored, scalable, and self-healing application deployment on Amazon EKS.

## Author

DevOps / Cloud Engineering Project
