# Conference Management Platform

**Conference** is a web platform for managing and organizing conferences, built with Django. It allows users to register, create and view conferences, and access detailed information.

Technologies: 
    Python 3.13+,
    Django 5.2.5,
    PostgreSQL (database),
    HTML / CSS / Bootstrap (frontend),
    JavaScript.

Project structure:
```
Conference/
├─ conference/          # main app
│   ├─ static/
│   │   └─ conference/js/
│   ├─ templates/
│   └─ models.py
├─ config/              # Django settings
├─ media/               # uploaded files
├─ static/              # global static files
├─ manage.py
└─ requirements.txt
```

Installation:

Clone the repository and navigate into it: 
```bash
git clone https://github.com/Gleg0/Conference.git
cd Conference
```
Create and activate a virtual environment:
```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
```
Install dependencies:
```bash
pip install -r requirements.txt
Set environment variables (e.g., in .env file):
```
Set environment variables (e.g., in .env file):
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/db_name

Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

Create a superuser:
```bash
python manage.py createsuperuser
```
Start the development server:
```bash
python manage.py runserver
```