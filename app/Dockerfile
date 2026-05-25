# Stage 1: Build dependency wheel layers (Explicit alias declaration)
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Minimal runtime image for production security
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed site-packages safely from the local builder stage
COPY --from=builder /root/.local /root/.local
COPY . .

# Path variables matching our folder layout
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/root/.local/lib/python3.11/site-packages
ENV PYTHONUNBUFFERED=1

EXPOSE 8080 8081 8082

CMD ["sh", "-c", "python ${APP_SCRIPT}"] 