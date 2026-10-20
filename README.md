# AetherForge

A cloud-integrated agentic AI research prototype.

## First milestone goal

Deploy a containerized application on AWS EC2, collect operational metrics with Prometheus, visualize them in Grafana, and generate evidence-based recommendations from the collected telemetry.

## Architecture

- AWS EC2
- Docker and Docker Compose
- Flask application
- Prometheus
- Grafana
- k6 or Locust for controlled traffic generation
- Python analysis service

## Team responsibilities

### Rohith — Cloud infrastructure and deployment

- AWS cloud environment setup
- Docker-based application deployment
- Application hosting and networking
- Prometheus metrics collection
- Grafana monitoring dashboard

### Intern 2 — Telemetry analysis and backend

- Application metric integration
- Python analysis service
- Prometheus query integration
- Threshold-based detection
- Evidence-based recommendations

## Safety principle

The prototype can generate recommendations, but it must not automatically modify cloud infrastructure.
