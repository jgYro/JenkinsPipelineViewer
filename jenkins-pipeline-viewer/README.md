# Jenkins Pipeline Viewer

A React application that provides real-time visualization of Jenkins CI/CD pipelines using WebSocket connections.

## Features

- **Real-time Updates**: Live pipeline status updates via WebSocket
- **Pipeline Visualization**: Beautiful UI similar to Jenkins Blue Ocean
- **Stage Progress**: Animated stage transitions with status indicators
- **Build Selector**: Switch between recent builds
- **Run Information**: Display build details including duration, trigger info, and timestamps
- **Step Details**: Expandable view of individual steps within each stage

## Prerequisites

- Node.js and npm installed
- Python Flask backend running on `http://localhost:5000`
- Jenkins server accessible with proper authentication

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The app will run on `http://localhost:3000`

## Backend Configuration

Make sure your Flask backend (`app.py`) is running and configured with:
- WebSocket support via Flask-SocketIO
- Proper Jenkins credentials
- CORS enabled for the React app

## Usage

1. Start your Flask backend server
2. Start the React application
3. The app will automatically connect to the WebSocket server
4. Pipeline data will be displayed and updated in real-time
5. Use the build selector to switch between different pipeline runs
6. Click the refresh button to manually request updates

## Technologies Used

- React with TypeScript
- Socket.IO Client for WebSocket connections
- Framer Motion for animations
- Lucide React for icons
- CSS with dark theme inspired by Jenkins Blue Ocean
