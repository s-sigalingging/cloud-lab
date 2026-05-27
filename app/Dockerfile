FROM python:3.11-slim

WORKDIR /app

# Upgrade pip for stability
RUN pip install --no-cache-dir --upgrade pip

# 1. Copy requirements from your app/ directory and install them globally
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy the rest of your microservice python files
COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8080 8081 8082

# Start the runtime dynamically using your APP_SCRIPT variable
CMD ["sh", "-c", "python ${APP_SCRIPT}"] 