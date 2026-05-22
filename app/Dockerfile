FROM python:3.11-slim
WORKDIR ./app
COPY app.py .
RUN pip install --no-cache-dir flask
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 5000
CMD ["python", "app.py"]