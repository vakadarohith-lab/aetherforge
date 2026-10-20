
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY analysis_service.py .

EXPOSE 8001

CMD ["python", "analysis_service.py"]
