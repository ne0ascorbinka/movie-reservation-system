# movie-reservation-system
Movie Reservation System. The service will allow users to sign up, log in, browse movies, reserve seats for specific showtimes, and manage their reservations. The system will feature user authentication, movie and showtime management, seat reservation functionality, and reporting on reservations.

---

## 🚀 Running the project

You can run the project in **two ways**:

1. **Locally using Python virtual environment**
2. **Using Docker (recommended for consistency)**

---

### 1️⃣ Run locally with Python

#### Prerequisites

* Python **3.11+** installed
* PostgreSQL running locally (or accessible remotely)
* `pip` available

#### Steps

```bash
# 1. Clone the repo and switch the active directory to it
git clone https://github.com/ne0ascorbinka/movie-reservation-system.git
cd movie-reservation-system

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # on Linux/Mac
venv\Scripts\activate      # on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.template .env
# edit .env with your DB creds, secret key, etc.

# 5. Go to Django project root directory
cd movie_reservation_system

# 6. Run migrations
python manage.py migrate

# 7. Create a superuser
python manage.py createsuperuser

# 8. Run the development server
python manage.py runserver
```

App will be available at 👉 `http://127.0.0.1:8000/`

---

### 2️⃣ Run with Docker

#### Prerequisites

* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/)
* Docker Desktop (if on Windows/Mac)

#### Steps

```bash
# 1. Clone the repo
git clone https://github.com/yourname/movie_reservation_system.git
cd movie_reservation_system

# 2. Set up environment variables
cp .env.template .env
# edit .env with your DB creds, secret key, etc.

# 3. Build and run containers
docker compose up --build
```

This will:

* Build the Django app image
* Start a Postgres database
* Run Django automatically on `http://localhost:8000/`

#### Common commands

* Stop everything:

  ```bash
  docker compose down
  ```
* Stop and remove **volumes** (resets DB data):

  ```bash
  docker compose down -v
  ```

---

### ✅ Notes

* Update `.env` before first run (both in Python or Docker).
* If you change DB credentials, you’ll likely need to reset the Postgres volume:

  ```bash
  docker compose down -v && docker compose up --build
  ```
* To use default cinema setup, run the following command:

  ```bash
  python manage.py seed_movies
  ```

### 📄 Environment Variables
The application uses the following environment variables for configuration. You can set these in a `.env` file based on the provided `.env.template`.
- _DEBUG_: Set to `True` for development mode, `False` for production
- _SECRET_KEY_: Django secret key
- _ALLOWED_HOSTS_: List of allowed hosts
- _POSTGRES_DB_: Name of the PostgreSQL database
  - _POSTGRES_USER_: PostgreSQL database user
  - _POSTGRES_PASSWORD_: Password for the PostgreSQL user
  - _POSTGRES_HOST_: Hostname for the PostgreSQL server (keep it default for docker-compose)
  - _POSTGRES_PORT_: Port number for the PostgreSQL server (for postgres default is `5432`)
- _DJANGO_ENV_: Environment profile (`dev` or `prod`)
- _COMPOSE_PROFILES_: Docker Compose profiles to use (based on `DJANGO_ENV`)
- _USE_AZURE_STORAGE_: Set to `True` to enable Azure storage, `False` otherwise
  - _AZURE_ACCOUNT_NAME_: Azure storage account name
  - _AZURE_ACCOUNT_KEY_: Azure storage account key
  - _AZURE_CONTAINER_NAME_: Azure storage container name
  - _AZURE_CUSTOM_DOMAIN_: Custom domain for Azure storage
- _SECURE_SSL_REDIRECT_: Set to `True` to enforce HTTPS, `False` otherwise
- _SESSION_COOKIE_SECURE_: Set to `True` to secure session cookies, `False` otherwise
- _CSRF_COOKIE_SECURE_: Set to `True` to secure CSRF cookies, `False` otherwise
- _CSRF_TRUSTED_ORIGINS_: List of trusted origins for CSRF protection