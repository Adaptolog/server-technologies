FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


FROM python:3.11-slim

# Create non-root user
RUN addgroup --system --gid 1001 flaskgroup && \
    adduser --system --uid 1001 --gid 1001 flaskuser

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/flaskuser/.local/bin:$PATH"

WORKDIR /app

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache /wheels/*

# Copy application
COPY . .

# Set ownership
RUN chown -R flaskuser:flaskgroup /app
USER flaskuser

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$PORT/healthcheck || exit 1

# Run the application
CMD ["gunicorn", "--workers", "2", "--threads", "4", "--bind", "0.0.0.0:$PORT", "app:app"]