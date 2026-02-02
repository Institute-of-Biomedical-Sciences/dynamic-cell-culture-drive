# Installation and Startup Guide

This guide explains how to install and start the New Harvest Control Software services (backend and
frontend).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Backend Installation](#backend-installation)
- [Frontend Installation](#frontend-installation)
- [Docker Deployment](#docker-deployment)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)
- [Environmental Variables](#environment-variables)
- [Additional Resources](#additional-resources)

## Prerequisites

- **Python 3.12.3** (for backend)
- **Node.js 20+** and **npm** (for frontend)
- **Docker** and **Docker Compose** (optional, for containerized deployment)

## Windows DLL Installation (libusb)

When using the Windows operating system, the **libusb dynamic link library (DLL)** must be installed
before running the backend scripts.

### Prerequisites

- Windows operating system
- Administrative privileges

### Installation Steps

1. **Download libusb**

   Download **libusb version 1.0.22**.

   > Note: Functionality is not guaranteed with other libusb versions.

   <https://github.com/libusb/libusb/releases/download/v1.0.22/libusb-1.0.22.7z>

2. **Install the DLL for 64-bit Windows**

   2.1. For **64-bit systems**, copy `MS64/dll/libusb-1.0.dll` to `C:/Windows/System/libusb/x64/`

   2.2. For **32-bit systems**, copy `MS32/dll/libusb-1.0.dll` to `C:/Windows/System/libusb/x86/`

> Notes
>
> - Ensure the destination directories exist before copying the DLL files.
> - Restart any dependent applications after installation.

## Backend Installation

- **[Backend installation guide](./backend/README.md)** - How to install and start the backend

## Frontend Installation

- **[Frontend installation guide](./frontend/README.md)** - How to install and start the frontend

## Docker Deployment

### Create an .env file with environment variables

```dotenv
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_database_name

PGADMIN_EMAIL=your_email@example.com
PGADMIN_PASSWORD=your_pgadmin_password
```

### Using Docker Compose (Recommended)

1. If you are running the application on a **Linux-based OS**:

   From the project root directory:

   ```bash
   docker-compose -f docker-compose-lin.yml up --build
   ```

2. If you are running the application on a **Windows OS**:

   From the project root directory:

   ```bash
   docker-compose -f docker-compose-win.yml up --build
   ```

This will start both backend and frontend services:

- **Backend**: <http://localhost:8000>
- **Frontend**: <http://localhost:80>

### Creating a Windows Desktop Shortcut (Optional)

If you are using **Windows**, you may configure a batch script to start the required services and
automatically open the application in your web browser.

1. Edit the start-newharvest.bat file to point to the correct project directory:

   1.1. Replace **C:\Users\...\your-new-harvest-project-location** with the full path to your local
   New Harvest project directory.

2. Once the file has been configured, create a desktop shortcut as follows:

   2.1. Right-click on the desktop and select New → Shortcut.

   2.2. When prompted for the shortcut location, browse to and select the start-newharvest.bat file.

   2.3. Click Next, provide a name for the shortcut, and select Finish.

> Double-clicking the shortcut will start the Docker services and open the application at
> <http://localhost:5173> in your default web browser.

**NOTE!** Opened terminals have to stay open for the services to keep running.

### Individual Docker Containers

#### Backend

```bash
cd backend
docker build -t newharvest-backend .
docker run -p 8000:8000 newharvest-backend
```

#### Frontend

```bash
cd frontend
docker build -t newharvest-frontend .
docker run -p 80:80 newharvest-frontend
```

## Development Workflow

### Starting Both Services Locally

1. **Terminal - Backend**:

   ```bash
   cd backend
   source venv/bin/activate  # If using virtual environment
   uvicorn app.main:app --reload
   ```

2. **Terminal - Frontend**:

   ```bash
   cd frontend
   npm run dev
   ```

### Accessing the Application

1. Open <http://localhost:5173> in your browser
2. Click "Quick Login (admin/admin)" or enter credentials manually
3. You'll be redirected to the dashboard with motor controls

## Troubleshooting

### Backend Issues

- **Port already in use**: Change the port in `backend/app/config.py` or use `--port` flag
- **Import errors**: Ensure you're in the correct directory and virtual environment is activated
- **Missing dependencies**: Run `pip install -r requirements.txt` again

### Frontend Issues

- **Port already in use**: Vite will automatically try the next available port
- **CORS errors**: Ensure backend CORS settings in `backend/app/config.py` include your frontend URL
- **API connection errors**: Verify backend is running and accessible at <http://localhost:8000>

### Docker Issues

- **Build failures**: Ensure Docker is running and you have sufficient disk space
- **Network issues**: Check `docker-compose.yml` network configuration
- **Volume mounting**: Ensure file paths in docker-compose.yml are correct

## Production Deployment

### Backend Production

1. Set `DEBUG=false` in environment variables
2. Use a production WSGI server like Gunicorn:

   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

### Frontend Production

1. Build the application:

   ```bash
   npm run build
   ```

2. Serve the `dist` directory using a web server (nginx, Apache, etc.)
3. Configure reverse proxy for API calls

## Environment Variables

### Backend

| Variable     | Default                                | Description       |
| ------------ | -------------------------------------- | ----------------- |
| `SECRET_KEY` | `your-secret-key-change-in-production` | JWT secret key    |
| `DEBUG`      | `true`                                 | Enable debug mode |
| `HOST`       | `0.0.0.0`                              | Server host       |
| `PORT`       | `8000`                                 | Server port       |

### Frontend

The frontend uses Vite's proxy configuration. API base URL is configured in `vite.config.ts`.

## Additional Resources

- API Documentation: <http://localhost:8000/docs> (when backend is running)
- Backend README: `backend/README.md` (if exists)
- Frontend README: `frontend/README.md`
