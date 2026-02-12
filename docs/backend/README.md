# Control Software Backend (API)

Backend API for controlling stepper motors and monitoring real-time diagnostics for the New Harvest
Control System. Built with FastAPI and designed for hardware-integrated environments.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

## Features

- **Motor Control**: Sending the movement requests to the stepper motors, fetching the actual
  diagnostics data from the motors
- **Real-time Stepper Information**: Overview of stepper actions in charts

## Prerequisites

- Python 3.12.3
- Virtual environment (recommended)

### Setup

#### Install the required dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate # venv\Scripts\activate for Windows
pip install -r requirements.txt
```

### Configure Environment (Optional)

Create a `.env` file in the `backend` directory:

```env
SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

### Run DB Docker compose

```bash
cd ..
docker compose up -d --build
```

### Run the backend service

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Service Features

When service is initialized:

- 🔌 **Stepper Motors**: Attempts to initialize the connected stepper motor
- 📊 **Status Reporting**: Accurate hardware status reporting

## API Documentation

Once the backend is running, visit:

- **Interactive API Docs**: localhost:8000/docs
- **Alternative API Docs**: localhost:8000/redoc

## Troubleshooting

### Port Already in Use

If you get "Address already in use" errors:

```bash
# Kill process using the port
lsof -ti:8000 | xargs kill -9
```

### Virtual Environment Issues

If you get "No module named 'module-name'" errors:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```
