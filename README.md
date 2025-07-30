# Jenkins Pipeline Viewer

A real-time Jenkins pipeline visualization system using Flask backend with WebSocket support and a React frontend.

## Overview

This project consists of:
- **Flask Backend** (`app.py`): Connects to Jenkins Blue Ocean API and provides WebSocket updates
- **React Frontend** (`jenkins-pipeline-viewer/`): Beautiful UI for visualizing pipeline progress

## Configuration

The system is configured to monitor the **CC3** pipeline on the **master** branch.

### Backend Configuration
- Jenkins URL: `http://localhost:8080`
- Username: `Yro`
- API Token: `9106c1c8ffb9ca0ca3c5ee102791df0d`
- Pipeline: `CC3`
- Branch: `master`

## Quick Start

### Option 1: Use the start script
```bash
./start_pipeline_viewer.sh
```

This will start both the Flask backend and React frontend automatically.

### Option 2: Manual start

1. Start the Flask backend:
```bash
python app.py
```

2. In a new terminal, start the React frontend:
```bash
cd jenkins-pipeline-viewer
npm start
```

## Features

- **Real-time Updates**: WebSocket connection for live pipeline status
- **Stage Visualization**: Shows all pipeline stages with status indicators
- **Step Details**: Expandable view of individual steps within each stage
- **Build Selector**: Switch between recent builds
- **Animations**: Smooth transitions when pipeline status changes
- **Dark Theme**: Inspired by Jenkins Blue Ocean

## API Endpoints

### WebSocket Events
- `connect`: Initial connection, sends current pipeline state
- `pipeline_update`: Broadcasts pipeline changes to all clients
- `switch_build`: Request to view a different build
- `request_update`: Manual refresh request

### Data Structure
```json
{
  "stages": [
    {
      "name": "Setup",
      "status": "SUCCESS",
      "stageFlowNodes": [
        {
          "name": "Check out from version control",
          "status": "SUCCESS"
        }
      ]
    }
  ],
  "runInfo": {
    "id": "1",
    "status": "SUCCESS",
    "durationMillis": 12345
  },
  "recentRuns": [...]
}
```

## Testing

To test the Flask API directly:
```bash
python test_api.py
```

To verify Jenkins connectivity:
```bash
./jenkins.sh
```

## Troubleshooting

1. **Connection Issues**: Ensure Jenkins is running on `http://localhost:8080`
2. **Authentication**: Verify the API token is correct
3. **CORS**: The Flask backend is configured to accept connections from any origin
4. **WebSocket**: Make sure your firewall allows WebSocket connections on port 5001
5. **Port Conflict**: If port 5001 is in use, update both `app.py` and `WebSocketContext.tsx`