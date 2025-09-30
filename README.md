# movie-reservation-system
Movie Reservation System. The service will allow users to sign up, log in, browse movies, reserve seats for specific showtimes, and manage their reservations. The system will feature user authentication, movie and showtime management, seat reservation functionality, and reporting on reservations.

## How to Run the Project
1. Clone the repository:
   ```bash
   git clone https://github.com/ne0ascorbinka/movie-reservation-system.git
   ```
2. Install the required dependencies:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Go to the project directory:
   ```bash
   cd movie-reservation-system
   ```
4. Apply migrations to set up the database:
   ```bash
   python manage.py migrate
   ```
5. Create a superuser to access the admin panel (if needed):
   ```bash
   python manage.py createsuperuser
   ```
6. Run the application:
   ```bash
   python manage.py runserver
   ```
7. Open your web browser and go to `http://localhost:8000` to access the application. 
   You can also access the admin panel at `http://localhost:8000/admin` using the superuser credentials you created.