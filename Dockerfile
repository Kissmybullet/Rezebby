FROM python:3.10-slim-bullseye

ENV PIP_NO_CACHE_DIR 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies including FFmpeg, Opus, build essentials
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libopus0 \
    libopus-dev \
    git \
    curl \
    wget \
    gcc \
    g++ \
    make \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libwebp-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application files
COPY . /app

# Upgrade pip and install Python requirements
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel && \
    pip3 install --no-cache-dir -r requirements.txt

# Start Bot
CMD ["python3", "-m", "LazyDeveloperr"]
