import os
import time
from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Self-Healing DevOps Service", version="1.0.0")

APP_ENV = os.getenv("ENVIRONMENT", "development")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests processed",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)


@app.middleware("http")
async def track_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    if request.url.path != "/metrics":
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path,
        ).observe(duration)

    return response


@app.get("/")
def root():
    return {
        "service": "fastapi-selfheal",
        "status": "running",
        "environment": APP_ENV,
        "version": APP_VERSION,
    }


@app.get("/healthz")
def liveness():
    return {"status": "alive"}


@app.get("/ready")
def readiness():
    return {"status": "ready", "environment": APP_ENV}


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
