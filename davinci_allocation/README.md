# Da Vinci Teacher Allocation System

This application automates the process of allocating teachers to Da Vinci program students at CGA.

## Features

- Automatic processing of student job forms
- Subject parsing and separation
- Teacher matching algorithm based on availability and workload
- Automated email notifications
- Dashboard for monitoring allocation status

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure environment variables in `.env` file:
   ```
   CRIMSON_APP_API_KEY=your_api_key
   EMAIL_SERVER=smtp.example.com
   EMAIL_USER=your_email@example.com
   EMAIL_PASSWORD=your_email_password
   ```

3. Run the application:
   ```
   python app.py
   ```

## System Components

- Data Integration: Connects to job form spreadsheets and Crimson App
- Teacher Matching: Algorithm to find optimal teacher matches
- Automated Workflow: Process management from form to confirmation
- Dashboard: Monitoring and management interface

## Usage

Access the dashboard at http://localhost:5000 to view and manage allocations. 