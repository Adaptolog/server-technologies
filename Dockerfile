FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-slim

RUN addgroup --system --gid 1001 flaskgroup && \
    adduser --system --uid 1001 --gid 1001 flaskuser

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/flaskuser/.local/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY . .

# Make init script executable
RUN chmod +x /app/init_db.sh

RUN chown -R flaskuser:flaskgroup /app
USER flaskuser

EXPOSE $PORT

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$PORT/healthcheck || exit 1

# Run init script and then start the app
CMD ["sh", "-c", "/app/init_db.sh && gunicorn --workers 2 --threads 4 --bind 0.0.0.0:$PORT wsgi:app"]