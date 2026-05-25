# Stage 2: Minimal runtime image for production security
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed site-packages from the builder layer
COPY --from=builder /root/.local /root/.local
COPY . .

# Add PYTHONPATH here alongside the existing PATH variable!
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/root/.local/lib/python3.11/site-packages
ENV PYTHONUNBUFFERED=1

EXPOSE 8080 8081 8082

CMD ["sh", "-c", "python app/${APP_SCRIPT}"]