#!/bin/bash

echo "Starting Jenkins Pipeline Viewer..."
echo ""

# Start Flask backend in background
echo "Starting Flask backend on port 5001..."
cd /Users/jerichogregory/Yro/projects/Maximus/C-SEA/JenkinsTesting
python app.py &
FLASK_PID=$!
echo "Flask backend started with PID: $FLASK_PID"

# Wait a bit for Flask to start
sleep 3

# Start React frontend
echo ""
echo "Starting React frontend on port 3000..."
cd /Users/jerichogregory/Yro/projects/Maximus/C-SEA/JenkinsTesting/jenkins-pipeline-viewer
npm start &
REACT_PID=$!
echo "React frontend started with PID: $REACT_PID"

echo ""
echo "Both services are running!"
echo "Flask backend: http://localhost:5001"
echo "React frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $FLASK_PID 2>/dev/null
    kill $REACT_PID 2>/dev/null
    echo "Services stopped."
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup INT

# Wait indefinitely
while true; do
    sleep 1
done