"""Minimal AetherForge service with Prometheus-compatible telemetry."""

from __future__ import annotations

import os
import time

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = Flask(__name__)

REQUEST_COUNT = Counter("aetherforge_http_requests_total", "Total HTTP requests handled by AetherForge.", ["method", "endpoint", "status"])
REQUEST_DURATION = Histogram("aetherforge_http_request_duration_seconds", "Time spent serving AetherForge HTTP requests.", ["method", "endpoint"])
WORK_ITEMS = Counter("aetherforge_work_items_total", "Controlled work requests completed by AetherForge.")

def tracked(endpoint: str):
    def decorator(view):
        def wrapped(*args, **kwargs):
            started = time.perf_counter()
            response = view(*args, **kwargs)
            status = response[1] if isinstance(response, tuple) else 200
            REQUEST_COUNT.labels(request.method, endpoint, str(status)).inc()
            REQUEST_DURATION.labels(request.method, endpoint).observe(time.perf_counter() - started)
            return response
        wrapped.__name__ = view.__name__
        return wrapped
    return decorator

@app.get("/")
@tracked("/")
def index():
    return jsonify(service="aetherforge", status="running")

@app.get("/health")
@tracked("/health")
def health():
    return jsonify(status="healthy")

@app.get("/api/work")
@tracked("/api/work")
def work():
    try:
        duration = float(request.args.get("duration", "0.1"))
    except ValueError:
        return jsonify(error="duration must be a number between 0 and 2"), 400
    if not 0 <= duration <= 2:
        return jsonify(error="duration must be a number between 0 and 2"), 400
    time.sleep(duration)
    WORK_ITEMS.inc()
    return jsonify(status="completed", duration_seconds=duration)

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
