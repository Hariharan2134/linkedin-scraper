FROM python:3.10-slim

# Install system dependencies for Chrome + Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    && apt-get clean

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV DISPLAY=:99

# Setup working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install pip packages
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files (ignore if fails)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Start server via gunicorn
CMD ["gunicorn", "linkedin_scraper.wsgi:application", "--bind", "0.0.0.0:8000"]
