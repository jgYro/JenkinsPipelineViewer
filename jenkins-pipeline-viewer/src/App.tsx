import React from 'react';
import { WebSocketProvider } from './contexts/WebSocketContext';
import PipelineVisualization from './components/PipelineVisualization';
import './App.css';

function App() {
  return (
    <WebSocketProvider>
      <PipelineVisualization />
    </WebSocketProvider>
  );
}

export default App;
