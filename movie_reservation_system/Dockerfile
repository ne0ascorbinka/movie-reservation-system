# Use a lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (needed for psycopg2-binary and Django)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Default environment
ENV DJANGO_ENV=prod
ENV POSTGRES_HOST=db

# Command: switch between dev and prod
CMD if [ "$DJANGO_ENV" = "dev" ]; then \
        python manage.py migrate && \
        python manage.py runserver 0.0.0.0:8000; \
    else \
        if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then \
            echo "Running migrations..." && \
            python manage.py migrate --noinput; \
        fi && \
        python manage.py collectstatic --noinput && \
        if [ "${CREATE_SUPERUSER:-false}" = "true" ]; then \
            echo "Creating superuser..." && \
            python manage.py createsuperuser --noinput \
                --username "$DJANGO_SUPERUSER_USERNAME" \
                --email "$DJANGO_SUPERUSER_EMAIL"; \
        fi && \
        exec gunicorn movie_reservation_system.wsgi:application \
            --bind 0.0.0.0:8000 \
            --workers 2; \
    fi