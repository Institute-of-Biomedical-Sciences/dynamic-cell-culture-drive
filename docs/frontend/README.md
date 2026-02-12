# Control Software User Interface

The user interface for controlling the system and it's individual components. Enables
real-time component data, health monitoring and component control.

## Features

- **Motor Control**: Controlling the stepper motor movements
- **Motor Statistics**: Real-time motor action statistics

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

**Install necessary node modules, with the commands:**

```bash
cd frontend
npm install
```

**Run the frontend service:**

```bash
npm start / or npm run dev
```

**Stop the frontend service:**

The frontend service can be stopped by pressing CTRL + C.

### Default Credentials

- **Username**: `admin`
- **Password**: `admin`

## Troubleshooting

### Port Already in Use

If you get "Address already in use" errors:

```bash
# Kill process using the port
lsof -ti:5173 | xargs kill -9
```

### Frontend Dependencies

If you get npm errors:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```
