# Stage 1: build dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
# copy root requirements.txt (was incorrectly backend/requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: final image
FROM python:3.11-slim
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy your backend code
COPY backend/app ./app
COPY data ./data

# Set Python path and expose port
ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
