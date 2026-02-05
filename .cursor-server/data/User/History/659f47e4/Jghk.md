# Backend Management Scripts

This directory contains three main scripts for managing the AI Agent Backend services.

## Available Scripts

### 1. `start_backend.sh`
Starts all backend services.

**Usage:**
```bash
./start_backend.sh
```

**Features:**
- Checks if backend is already running
- Detects Python version automatically (prefers Python 3.11)
- Installs/updates dependencies
- Starts uvicorn server on port 8000
- Verifies successful startup
- Shows status and logs

### 2. `stop_backend.sh`
Stops all backend services.

**Usage:**
```bash
./stop_backend.sh
```

**Features:**
- Kills all uvicorn processes
- Frees port 8000
- Verifies all processes are stopped
- Handles multiple process patterns

### 3. `restart_backend.sh`
Restarts all backend services (stops then starts).

**Usage:**
```bash
./restart_backend.sh
```

**Features:**
- Stops all services first
- Waits for clean shutdown
- Starts services fresh
- Complete restart cycle

## Quick Start

```bash
# Start backend
./start_backend.sh

# Stop backend
./stop_backend.sh

# Restart backend
./restart_backend.sh
```

## Troubleshooting

### Port 8000 already in use
If you get an error about port 8000 being in use:
```bash
# Stop the backend first
./stop_backend.sh

# Or manually free the port
sudo lsof -ti:8000 | xargs sudo kill -9
```

### Need root privileges
Some operations may require sudo:
```bash
sudo ./stop_backend.sh
```

### Check if backend is running
```bash
# Check processes
ps aux | grep uvicorn

# Check port
lsof -i:8000
```

### View logs
```bash
tail -f backend.log
```

## Notes

- All scripts are executable and can be run directly
- Scripts automatically detect Python version
- Logs are written to `backend.log`
- Backend runs on port 8000 by default
- API documentation available at: http://localhost:8000/docs

