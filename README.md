# Da Vinci Teacher Allocation System

A sophisticated automation solution for managing teacher allocations in the Da Vinci program. This system streamlines the process of matching students with teachers, handling multi-subject allocations, and managing communications.

## Features

### 1. Intelligent Teacher Matching
- Sophisticated matching algorithm considering:
  - Subject expertise and qualifications
  - Current workload and availability
  - Student preferences and schedule compatibility
  - Historical performance metrics
- Real-time workload monitoring
- Automated teacher invitations

### 2. Web Interface
- Real-time dashboard for tracking allocations
- Detailed views of student-teacher matches
- Easy-to-use forms for creating new allocations
- Status tracking and progress monitoring
- Clean, intuitive design

### 3. Crimson API Integration
- Seamless integration with Crimson platform
- Automated teacher invitations
- Real-time workload monitoring
- Student subject management
- Status updates and confirmations

### 4. Data Processing
- Efficient handling of multi-subject allocations
- Data validation and transformation
- Status tracking and updates
- Performance analytics
- Automated data splitting for multiple subjects

### 5. Communication System
- Automated email notifications
- Personalized communications
- Multi-party notification management
- Templated messages for consistency
- Delivery and engagement tracking

## Setup

### Prerequisites
- Python 3.8 or newer
- pip (Python package manager)
- Git (for cloning the repository)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/none34829/cga-assignment
cd davinci-allocation
```

2. Create a `.env` file in the root directory with the following settings:
```
CRIMSON_API_KEY=your_api_key_here
CRIMSON_API_URL=https://api.crimsoneducation.org/v1
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=your_email@gmail.com
```

3. Run the application:

On Windows:
```bash
run.bat
```

On Linux/Mac:
```bash
./run.sh
```

The setup script will:
- Check for Python and pip installation
- Install required packages
- Create necessary data folders
- Start the application

## Project Structure

```
davinci_allocation/
├── app/
│   ├── __init__.py
│   ├── app.py              # Main Flask application
│   ├── models.py           # Data models
│   ├── data_processor.py   # Data processing logic
│   ├── teacher_matcher.py  # Teacher matching algorithm
│   ├── crimson_api.py      # Crimson API integration
│   └── email_service.py    # Email notification system
├── templates/
│   ├── dashboard.html      # Main dashboard
│   ├── allocation_details.html
│   ├── new_allocation.html
│   └── email_templates.py
├── data/                   # Application data
├── test_data/             # Test data
├── run.bat                # Windows startup script
├── run.sh                 # Unix startup script
└── requirements.txt       # Python dependencies
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Mock Data
The system includes mock data for development and testing. To use mock data:
1. Set `USE_MOCK=true` in your `.env` file
2. The system will use mock data instead of making real API calls

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request