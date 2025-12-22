FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including Playwright dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    wget \
    curl \
    fonts-dejavu \
    fonts-liberation \
    xfonts-encodings \
    xfonts-utils \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libatspi2.0-0 \
    libxrandr2 \
    libxinerama1 \
    libxcursor1 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libglib2.0-0 \
    libxdamage1 \
    libxcomposite1 \
    libxext6 \
    libx11-6 \
    libdrm2 \
    libgbm1 \
    libasound2 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install chromium

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application with hot-reload enabled
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
