# Multi-Tenant Grading App

A web application for teachers to manage grading, schools, classrooms, and students. Built with Flask and SQLite.

## Features
- Teacher account creation and login
- Manage up to 5 schools per teacher
- Manage up to 20 classrooms per teacher (each classroom linked to a school)
- Manage up to 100 students per classroom
- Import students via CSV

## Tech Stack
- Python 3.x
- Flask
- Flask-Login
- Flask-SQLAlchemy
- SQLite
- Bootstrap (for UI)

## Setup Instructions
1. Clone the repository
2. Create a virtual environment and activate it
3. Install dependencies: `pip install -r requirements.txt`
4. Run the app: `flask run`

## Project Structure
```
grading-app/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   ├── templates/
│   └── static/
├── migrations/
├── requirements.txt
├── README.md
└── run.py
```

## CSV Import Format
- CSV must have columns: `first_name`, `last_name`

## License
MIT
