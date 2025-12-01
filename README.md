# linkedin_scraper (Django)
This is a minimal Django project containing a simple login page, dashboard, and a placeholder for a LinkedIn Selenium scraper.

## How to use
1. Create a virtual environment and install Django:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install django
   ```
2. Run migrations and create a superuser:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
3. Run the development server:
   ```bash
   python manage.py runserver
   ```
4. Visit http://127.0.0.1:8000/ to see the login page.

## Notes
- The scraper is a placeholder at `scraper_app/real_scraper.py`. Replace it with your Selenium code.
