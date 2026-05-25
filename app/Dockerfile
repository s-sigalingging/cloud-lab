# Stage 1: Build dependency wheel layers
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

# Copy installed site-packages from the builder layer
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Expose all ports used across our bank service layers
EXPOSE 8080 8081 8082

# The default startup command uses a generic shell wrapper 
# that allows us to pass different scripts during runtime execution!
CMD ["sh", "-c", "python ${APP_SCRIPT}"]