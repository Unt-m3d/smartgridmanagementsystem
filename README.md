#  Smart Grid Management System
A real time energy management system that monitors and controls power distribution. Built with Django, REST Framework, and Chart.js.

This system monitors electrical parameters in real time, allows remote control of devices, detects unsafe conditions, and calculates energy costs automatically. It helps users reduce energy waste and integrate renewable energy sources.

##  Features

Core Features:
-  Real-Time Monitoring - Live energy data every 3 seconds  
-  Device Control - Turn devices ON/OFF with persistent state  
-  Smart Alerts - Automatic detection of anomalies  
-  Live Charts - Real-time visualization with Chart.js  
-  Data Validation - All input validated (no negative values)  
-  Error Handling - Comprehensive logging and error responses  
-  Admin Panel - Django admin for data management  
-  Pagination - Efficient API data retrieval (max 1000 records)

NEW UPGRADES:
-  Energy Graphs - Visualize energy trends over time
- AI Predictions - Forecast future energy usage using machine learning
-  SMS/Email Alerts - Get notifications when thresholds are exceeded
- Renewable Energy Integration- Track solar, wind, and other renewable sources
-  Analytics Dashboard - Comprehensive statistics and reporting

##  Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Redis (for Celery async tasks)

### Installation

```bash
# Clone the repo
git clone https://github.com/Unt-m3d/smartgridmanagementsystem.git
cd smartgridmanagementsystem

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user (optional)
python manage.py createsuperuser

# Start Redis (in another terminal)
redis-server

# Start Celery worker (in another terminal)
celery -A backend worker -l info

# Start Celery beat (in another terminal, for scheduled tasks)
celery -A backend beat -l info

# Start server
python manage.py runserver