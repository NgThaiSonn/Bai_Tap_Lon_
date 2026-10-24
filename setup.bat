@echo off
REM
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations accounts catalog orders
python manage.py migrate
python manage.py runserver
