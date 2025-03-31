@echo off
echo starting up da vinci allocation system...

:: check if we have python installed
python --version >nul 2>&1
if errorlevel 1 (
    echo oops! looks like python isn't installed
    echo please install python 3.8 or newer from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: check if we have pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo uh oh! pip isn't installed
    echo please install pip from https://pip.pypa.io/en/stable/installation/
    pause
    exit /b 1
)

:: make sure we have all the packages we need
echo getting all the packages we need...
pip install -r requirements.txt

:: check if we have a .env file
if not exist .env (
    echo hey! we need a .env file
    echo please create one with these settings:
    echo CRIMSON_API_KEY=your_api_key_here
    echo CRIMSON_API_URL=https://api.crimsoneducation.org/v1
    echo SMTP_SERVER=smtp.gmail.com
    echo SMTP_PORT=587
    echo SMTP_USERNAME=your_email@gmail.com
    echo SMTP_PASSWORD=your_app_password
    echo SENDER_EMAIL=your_email@gmail.com
    pause
    exit /b 1
)

:: make sure we have our data folder
if not exist data (
    echo creating data folder...
    mkdir data
)

:: make sure we have our test data folder
if not exist test_data (
    echo creating test data folder...
    mkdir test_data
)

:: run the app
echo starting the app...
python app.py

pause 