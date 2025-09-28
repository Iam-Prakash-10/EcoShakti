@echo off
echo Starting EcoShakti Production Deployment...

REM Create logs directory
if not exist "logs" mkdir logs

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install gunicorn eventlet

REM Set production environment variables
set FLASK_ENV=production
set FLASK_DEBUG=0

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    echo FLASK_SECRET_KEY=your_production_secret_key_here > .env
    echo DATABASE_URL=sqlite:///energy_monitor.db >> .env
    echo ML_MODEL_PATH=./ml_models >> .env
    echo FLASK_ENV=production >> .env
)

REM Start the application
echo Starting EcoShakti with Gunicorn...
gunicorn --config gunicorn.conf.py app:app

pause