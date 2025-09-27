# ALX Project Nexus - Setup Guide

## Overview

This guide walks you through setting up the ALX Project Nexus Django application on your local machine for development purposes.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- Git
- Command line interface (Terminal, PowerShell, or Command Prompt)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd alx-project-nexus
```

### 2. Create Virtual Environment

Create an isolated Python environment for the project:

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` or similar prefix in your terminal prompt indicating the virtual environment is active.

### 4. Install Dependencies

Install all required packages using the working requirements file:

```bash
pip install -r requirements-working.txt
```

**Important:** Use `requirements-working.txt` instead of `requirements/base.txt` as it includes all necessary dependencies including `dj-database-url`.

### 5. Database Setup

Run the database migrations to set up the database schema:

```bash
python manage.py migrate
```

**Note:** You don't need to run `makemigrations` as the migration files are already included in the repository.

### 6. Create Superuser (Optional)

If you want to access the Django admin interface, create a superuser account:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter username, email, and password.

### 7. Start Development Server

Launch the Django development server:

```bash
python manage.py runserver
```

## Accessing the Application

Once the server is running, you can access:

- **Main Application:** http://127.0.0.1:8000/
- **Admin Interface:** http://127.0.0.1:8000/admin/ (if superuser created)
- **API Documentation:** http://127.0.0.1:8000/api/schema/swagger-ui/ (if available)

## Project Structure

The project includes these main components:
- Django REST Framework for API development
- PostgreSQL database support (with SQLite fallback for development)
- Celery for background tasks
- GraphQL support
- JWT authentication
- API documentation with Spectacular

## Troubleshooting

### Common Issues

**ModuleNotFoundError for 'dj_database_url':**
- Ensure you're using `requirements-working.txt`
- Manually install if needed: `pip install dj-database-url`

**URL Namespace Warning:**
- You may see warnings about 'authentication' namespace not being unique
- This doesn't prevent the application from running

**Database Connection Issues:**
- The project is configured to work with SQLite by default for local development
- Check for `.env.example` file for environment variable requirements

## Development Workflow

1. Always activate your virtual environment before working on the project
2. Install new dependencies with `pip install <package-name>`
3. Update requirements if you add new packages
4. Run migrations after pulling new changes: `python manage.py migrate`
5. Use `python manage.py runserver` to test your changes

## Support

If you encounter issues not covered in this guide, check:
- Project README.md file
- Django documentation
- Project issue tracker

---

**Last Updated:** Based on successful setup process with Python 3.13.7 on Windows