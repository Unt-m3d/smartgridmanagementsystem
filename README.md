# Smart Grid Management System

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Django](https://img.shields.io/badge/Django-4.0+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

A comprehensive real-time energy management system that monitors and controls power distribution networks. Built with Django, Django REST Framework, and Chart.js for intelligent energy management and optimization.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Overview

Smart Grid Management System is designed to provide real-time monitoring and control of electrical energy distribution. It enables users to:

- Monitor electrical parameters in real-time (voltage, current, power)
- Control devices remotely (ON/OFF operations)
- Detect and alert on anomalies
- Predict energy consumption patterns using AI
- Track renewable energy sources
- Generate comprehensive energy reports

The system is ideal for residential, commercial, and industrial energy management applications.

## Features

### Core Features

- **Real-Time Monitoring** - Live energy data updated every 3 seconds
- **Device Control** - Remote ON/OFF device management with persistent state
- **Smart Alerts** - Automatic anomaly detection with configurable thresholds
- **Live Charts** - Real-time data visualization using Chart.js
- **Data Validation** - Comprehensive input validation (no negative values)
- **Error Handling** - Robust error handling with comprehensive logging
- **Admin Panel** - Full Django admin interface for data management
- **Pagination** - Efficient API data retrieval (max 1000 records per request)

### Advanced Features

- **Energy Predictions** - AI-powered forecasting of future energy usage
- **SMS/Email Alerts** - Multi-channel notifications for critical events
- **Renewable Energy Integration** - Track solar, wind, and alternative energy sources
- **Analytics Dashboard** - Comprehensive statistics and reporting
- **Energy Trends** - Visual representation of energy patterns over time
- **Cost Analysis** - Automatic energy cost calculation and tracking

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Django 4.0+, Django REST Framework |
| Frontend | HTML5, CSS3, JavaScript, Chart.js |
| Database | SQLite (default), PostgreSQL (production) |
| Task Queue | Celery + Redis |
| Async Tasks | Celery Beat |
| Authentication | Django Auth |
| API Documentation | DRF Browsable API |

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package manager)
- Redis server (for Celery task queue)
- Git
- Virtual environment support

 # Smart Grid Management System 

Geoffrey Getaro – ENG - 219- 074/24
Tonny Otumba – ENG- 219 - 061/24
Abigael Mogusu – ENG- 219 -102/24
Danharry Gatere – ENG - 219-006/24
Wendy Knight – ENG – 219- 063/24
Jess Lesley – ENG – 219- 056/24
Kevin Manyonge – ENG – 219 – 053/24
Ephraim Mongare- ENG-219-030/24

---

##  Project Overview

The **Smart Grid Management System** is a web-based application designed to monitor, analyze, and manage energy usage in real time.

This project demonstrates how modern systems can:

* Collect energy data
* Process it efficiently
* Detect problems automatically
* Notify users instantly

It is especially useful for learning concepts in:

* Software engineering
* Backend development
* APIs and system integration
* Smart energy systems

---

##  Project Objectives (For Grading)

This system was developed to:

* ✔ Demonstrate real-time data handling
* ✔ Implement RESTful APIs using Django
* ✔ Use background processing (Celery)
* ✔ Simulate real-world IoT energy data
* ✔ Integrate external services (SMS notifications)
* ✔ Build a scalable and modular system

---

##  Technologies Used

| Component            | Technology            |
| -------------------- | --------------------- |
| Programming Language | Python                |
| Backend Framework    | Django                |
| API Framework        | Django REST Framework |
| Task Queue           | Celery                |
| Scheduler            | Celery Beat           |
| Messaging/Alerts     | Twilio,emails         |
| Testing Tool         | Postman               |
| Database             | SQLite / PostgreSQL   |
| Cache & Broker       | Redis                 |

---

##  System Architecture

The system follows a **distributed architecture**, where different components work together:

### 1. Backend Server

* Built using Django
* Handles data processing, storage, and API requests
* Acts as the **brain of the system**

### 2. APIs (Application Programming Interfaces)

* Allow communication between frontend and backend
* Enable sending and retrieving energy data
* Make integration with real devices possible

### 3. Background Task Processing

* Uses Celery
* Runs heavy tasks in the background
* Keeps the system fast and responsive

### 4. Task Scheduler

* Uses Celery Beat
* Runs tasks at fixed intervals
* Example: checking energy usage every minute

### 5. Data Simulator

* Generates sample energy data
* Useful when real sensors are not available

---

##  System Architecture Diagram

```
        ┌──────────────────────────┐
        │     Frontend (UI)        │
        │ Dashboard / Mobile View  │
        └──────────┬───────────────┘
                   │
                   ▼
        ┌──────────────────────────┐
        │     Django Backend       │
        │   (API + Logic Layer)    │
        └──────────┬───────────────┘
                   │
     ┌─────────────┴─────────────┐
     ▼                           ▼
┌──────────────┐         ┌──────────────┐
│  Database    │         │    Redis     │
│ (Storage)    │         │ (Cache/Queue)│
└──────────────┘         └──────┬───────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
           ┌────────┐    ┌──────────┐    ┌─────────┐
           │ Worker │    │ Scheduler│    │  Tasks  │
           │Celery  │    │  Beat    │    │ Queue   │
           └────────┘    └──────────┘    └─────────┘
```

---

##  Key Technologies Explained (Simple)

### 🔹 Django

Handles the backend logic, database, and APIs.

### 🔹 Celery

Processes tasks in the background (e.g., sending alerts).

### 🔹 Redis

Acts as a message broker between Django and Celery.

### 🔹 Twilio

Sends SMS alerts to users in real time.
 goal==(to make the non smartphone users be able to get alerts too)

### 🔹 Postman

Used to test APIs during development.

---

##  Role of External Tools

### Twilio (goal==(to make the non smartphone users be able to get alerts too))

Used to send SMS notifications such as:

* Power outages
* System faults
* High energy usage

This ensures users receive updates instantly.

---

### Postman

Used for testing APIs:

* Send requests
* View responses
* Debug errors

Helps ensure everything works correctly before deployment.

---

##  How the System Works (Step-by-Step)

1. The **data simulator** or device generates energy data
2. Data is sent to the backend through APIs
3. The backend stores and processes the data
4. The system checks for abnormal conditions
5. If a problem is detected:

   * A background task is triggered
   * An alert is generated
   * SMS is sent using Twilio
6. Users view results on the dashboard

---

##  Installation Guide (Simple Steps)

### 1. Clone the Project

```bash
git clone https://github.com/Unt-m3d/smartgridmanagementsystem.git
cd smartgridmanagementsystem
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings.

---

### 5. Setup Database

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

### 6. Run the System

Open 4 terminals:

**Terminal 1**

```bash
redis-server
```

**Terminal 2**

```bash
celery -A backend worker -l info
```

**Terminal 3**

```bash
celery -A backend beat -l info
```

**Terminal 4**

```bash
python manage.py runserver
```

---

##  Access the System

* Main Dashboard: http://localhost:8000
* Admin Panel: http://localhost:8000/admin
* API: http://localhost:8000/api

---

##  Testing the System

Run the simulator:

```bash
python simulate_data.py
```

This generates fake energy data every few seconds.

---

##  Example API Output

```json
{
  "voltage": 230.5,
  "current": 2.3,
  "power": 530.15
}
```

---

## Project Structure (Simplified)

```
smartgridmanagementsystem/
│
├── backend/        → Main project settings
├── energy/         → Energy data logic
├── notifications/  → Alerts & SMS system
├── frontend/       → User interface
├── simulate_data.py
└── manage.py
```

---

##  Key Learning Outcomes
apart from making the problem solving aspect of every engineer this project will help an upcoming programmer understand 
the following: 

* How APIs work in real systems
* How to build scalable backend applications
* How background processing improves performance
* How real-world systems handle data and alerts
* How different technologies integrate together
 *Understand how to interact with other wedsites in building a project e.g for this case twillio and postman agent


---

##  Conclusion

This project demonstrates how software can be used to solve real-world problems in energy management. It combines multiple technologies into a single working system and provides a strong foundation for advanced projects in:

* Smart systems
* IoT applications
* Data-driven platforms

---

##  Final Note

TThe system uses a multi-provider notification architecture with failover mechanisms and asynchronous task queues to ensure reliable delivery under failure conditions.

made by the group 2 
---
    
