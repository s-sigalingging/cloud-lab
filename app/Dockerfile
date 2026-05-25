# Stage 1: Build dependency wheel layers
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install packages directly into the standard system path in the builder stage
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Minimal runtime image for production security
FROM python:3.11-slim AS runtime

WORKDIR /app

# COPY FIX: Copy packages straight into Python's global site-packages directory
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy your actual Python application scripts
COPY . .

# Keep the environment clean and unbuffered
ENV PYTHONUNBUFFERED=1

EXPOSE 8080 8081 8082

# Simplified, reliable runtime startup execution
CMD ["sh", "-c", "python ${APP_SCRIPT}"]