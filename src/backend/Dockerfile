FROM python:3.12-slim

# Keep Python output unbuffered
ENV PYTHONUNBUFFERED=1

# Use /app as working directory
WORKDIR /app

# Install system deps including GCC
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential ca-certificates wget \
    && rm -rf /var/lib/apt/lists/*

# Install python deps
# When building with context `./backend`, requirements.txt is at the root of the context
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend source (context is ./backend)
COPY . /app

# Ensure database directory exists and is writable
RUN mkdir -p /app/data \
    && chown -R root:root /app

VOLUME ["/app/data"]

ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONPATH=/app

EXPOSE 5000

CMD ["python", "app.py"]
