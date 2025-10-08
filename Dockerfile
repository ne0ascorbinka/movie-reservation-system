# Use a lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Make inner project and repo root visible first on sys.path
ENV PYTHONPATH=/app/movie_reservation_system:/app

# Set work directory
WORKDIR /app

# Install system dependencies (needed for psycopg2-binary and Django)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Default environment
ENV DJANGO_ENV=prod

# Command: switch between dev and prod
CMD if [ "$DJANGO_ENV" = "dev" ]; then \
        python movie_reservation_system/manage.py migrate && \
        python movie_reservation_system/manage.py runserver 0.0.0.0:8000; \
    else \
        python movie_reservation_system/manage.py migrate && \
        gunicorn movie_reservation_system.wsgi:application \
                 --bind 0.0.0.0:8000 --workers 4; \
    fi