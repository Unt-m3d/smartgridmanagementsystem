#  Smart Grid Management System
A real time energy management system that monitors and controls power distribution. Built with Django, REST Framework, and Chart.js.
This system monitors electrical parameters in real time, allows remote control of devices, detects unsafe conditions, and calculates energy costs automatically. It helps users reduce energy waste, prevent equipment damage, and manage electricity expenses efficiently

##  Features

  Real-Time Monitoring - Live energy data every 3 seconds  
  Device Control - Turn devices ON/OFF with persistent state  
 Smart Alerts - Automatic detection of anomalies  
 Live Charts- Real-time visualization with Chart.js  
 Data Validation - All input validated (no negative values)  
 Error Handling - Comprehensive logging and error responses  
 Admin Panel- Django admin for data management  
 Pagination - Efficient API data retrieval (max 1000 records)  



##  Quick Start

### Prerequisites
 Python 3.8+
 pip (Python package manager)

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

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user (optional)
python manage.py createsuperuser

# Start server
python manage.py runserver