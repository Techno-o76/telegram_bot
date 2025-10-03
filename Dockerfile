# syntax=docker/dockerfile:1

# Use Python 3.12 (stable for python-telegram-bot)
FROM python:3.12-slim

# Prevent .pyc files and enable direct logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# (Optional) non-root user if you want
# RUN adduser --disabled-password --gecos "" appuser
# USER appuser

# No ports exposed (we use polling, not webhooks)
# EXPOSE 8000

# Run the bot
CMD ["python", "main.py"]
