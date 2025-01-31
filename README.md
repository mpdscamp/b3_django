# B3 Monitor

Real-time monitoring system for B3 (Brazil Stock Exchange) assets with customizable price tunnels and email alerts.

## Features

- Automated price monitoring with customizable intervals
- Email alerts when prices cross defined thresholds
- Interactive price charts and historical data
- User-specific asset tracking
- Flexible monitoring frequencies per asset

## Prerequisites

- Python 3.10 or higher
- Redis server
- An email account for email notifications

## Installation

1. Clone the repository:
```bash
git clone git@github.com:mpdscamp/b3_django.git
```

2. Install Poetry (if not installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. Create a .env file with your settings. For example:
```
# SECURITY
SECRET_KEY={your security key}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# DATABASE
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# CELERY
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# EMAIL SETTINGS
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER={email address}
EMAIL_HOST_PASSWORD={email app password}
DEFAULT_FROM_EMAIL={email address}
SERVER_EMAIL={email address}
EMAIL_DEBUG=True

```

5. Initialize database:
```bash
poetry run python manage.py migrate
```

6. Load initial B3 assets:
```bash
poetry run python manage.py populate_available_assets --file assets/data/b3_tickers.csv
```

## Running the System

1. Start Redis server:
```bash
redis-server
```

2. Start Celery worker:
```bash
poetry run celery -A b3_monitor worker --loglevel=info --pool=solo
```

3. Start Celery beat (in a separate terminal):
```bash
poetry run celery -A b3_monitor beat --loglevel=info
```

4. Run development server:
```bash
poetry run python manage.py runserver
```

Access the application at `http://localhost:8000`

## Email Configuration

1. Enable 2-factor authentication in your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → App passwords
   - Generate a new app password
3. Use this password in your .env file

## Architecture

- Django web framework
- Celery for asynchronous tasks
- Redis as message broker
- yfinance for fetching B3 data
