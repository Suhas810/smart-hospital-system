FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY backend/ backend/
COPY frontend/ frontend/
COPY run.py .

ENV PORT=8080

# Run with Gunicorn for production performance
# Workers=1 Threads=8 is a good default for I/O bound Flask apps on Cloud Run (1 vCPU)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 run:app
