#!/bin/bash

echo "starting up da vinci allocation system..."

# check if we have python installed
if ! command -v python3 &> /dev/null; then
    echo "oops! looks like python isn't installed"
    echo "please install python 3.8 or newer from https://www.python.org/downloads/"
    exit 1
fi

# check if we have pip
if ! command -v pip3 &> /dev/null; then
    echo "uh oh! pip isn't installed"
    echo "please install pip from https://pip.pypa.io/en/stable/installation/"
    exit 1
fi

# make sure we have all the packages we need
echo "getting all the packages we need..."
pip3 install -r requirements.txt

# check if we have a .env file
if [ ! -f .env ]; then
    echo "hey! we need a .env file"
    echo "please create one with these settings:"
    echo "CRIMSON_API_KEY=your_api_key_here"
    echo "CRIMSON_API_URL=https://api.crimsoneducation.org/v1"
    echo "SMTP_SERVER=smtp.gmail.com"
    echo "SMTP_PORT=587"
    echo "SMTP_USERNAME=your_email@gmail.com"
    echo "SMTP_PASSWORD=your_app_password"
    echo "SENDER_EMAIL=your_email@gmail.com"
    exit 1
fi

# make sure we have our data folder
if [ ! -d "data" ]; then
    echo "creating data folder..."
    mkdir data
fi

# make sure we have our test data folder
if [ ! -d "test_data" ]; then
    echo "creating test data folder..."
    mkdir test_data
fi

# run the app
echo "starting the app..."
python3 app.py 