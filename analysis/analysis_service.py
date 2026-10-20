
import math
import os

import requests
from flask import Flask, jsonify

app = Flask(__name__)

PROMETHEUS_URL = os.getenv(
    "PROMETHEUS_URL",
    "http://localhost:9090",
)

LATENCY_THRESHOLD_SECONDS = 0.5
ERROR_RATE_THRESHOLD = 0.05


def query_prometheus(promql):
    """Run a PromQL query and return its results."""
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": promql},
        timeout=5,
    )
    response.raise_for_status()

    payload = response.json()

    if payload.get("status") != "success":
        raise RuntimeError("Prometheus query was unsuccessful")

    return payload["data"]["result"]


def analyse_telemetry():
    """Analyse application latency and HTTP 5xx error rate."""
    recommendations = []
    evidence = {}

    # Average request latency over the last five minutes.
    latency_query = (
        'sum(rate(aetherforge_http_request_duration_seconds_sum'
        '{job="aetherforge-app"}[5m])) / '
        'sum(rate(aetherforge_http_request_duration_seconds_count'
        '{job="aetherforge-app"}[5m]))'
    )

    latency_result = query_prometheus(latency_query)

    if latency_result:
        latency = float(latency_result[0]["value"][1])
        if math.isfinite(latency):
            evidence["average_latency_seconds"] = round(latency, 4)

            if latency > LATENCY_THRESHOLD_SECONDS:
                recommendations.append({
                    "issue": "High average request latency",
                    "severity": "warning",
                    "observed_value_seconds": round(latency, 4),
                    "threshold_seconds": LATENCY_THRESHOLD_SECONDS,
                    "recommendation": (
                        "Inspect slow endpoints and investigate "
                        "application processing time."
                    ),
                })
        else:
            evidence["average_latency_seconds"] = None
    else:
        evidence["average_latency_seconds"] = None

    
        # HTTP 5xx error rate over the last five minutes.
    error_query = (
        '(sum(rate(aetherforge_http_requests_total'
        '{job="aetherforge-app",status=~"5.."}[5m])) or vector(0)) / '
        'sum(rate(aetherforge_http_requests_total'
        '{job="aetherforge-app"}[5m]))'
    )
    error_result = query_prometheus(error_query)

    if error_result:
        error_rate = float(error_result[0]["value"][1])

        if math.isfinite(error_rate):
            evidence["http_5xx_error_rate"] = round(error_rate, 4)

            if error_rate > ERROR_RATE_THRESHOLD:
                recommendations.append({
                    "issue": "Elevated HTTP 5xx error rate",
                    "severity": "critical",
                    "observed_value": round(error_rate, 4),
                    "threshold": ERROR_RATE_THRESHOLD,
                    "recommendation": (
                        "Inspect application logs and failed requests "
                        "to identify the cause of server errors."
                    ),
                })
        else:
            evidence["http_5xx_error_rate"] = None
    else:
        evidence["http_5xx_error_rate"] = None

    return {
        "service": "AetherForge Telemetry Analysis",
        "evidence": evidence,
        "recommendations": recommendations,
        "note": (
            "Recommendations only; no infrastructure changes are made."
        ),
    }


@app.get("/health")
def health():
    return jsonify(status="healthy")


@app.get("/analyse")
def analyse():
    try:
        return jsonify(analyse_telemetry())
    except requests.RequestException:
        return jsonify(error="Unable to reach Prometheus"), 502
    except (ValueError, KeyError, RuntimeError):
        app.logger.exception("Telemetry analysis failed")
        return jsonify(error="Telemetry analysis failed"), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8001")),
    )
