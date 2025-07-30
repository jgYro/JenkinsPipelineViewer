import React, { createContext, useContext, useEffect, useRef, useState, ReactNode } from 'react';
import { io, Socket } from 'socket.io-client';

interface Stage {
  name: string;
  status: string;
  startTimeMillis: number;
  durationMillis: number;
  stageFlowNodes: StageFlowNode[];
}

interface StageFlowNode {
  name: string;
  status: string;
  parameterDescription?: string;
}

interface RunInfo {
  id: string;
  name: string;
  status: string;
  startTimeMillis: number;
  durationMillis: number;
  queueDurationMillis: number;
  causesString: string;
}

interface RecentRun {
  id: string;
  name: string;
  status: string;
  startTimeMillis: number;
  durationMillis: number;
  queueDurationMillis: number;
}

interface PipelineData {
  stages: Stage[];
  runInfo: RunInfo;
  recentRuns: RecentRun[];
  isNewBuild?: boolean;
}

interface WebSocketContextType {
  pipelineData: PipelineData | null;
  isConnected: boolean;
  switchBuild: (runId: string) => void;
  requestUpdate: () => void;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
};

interface WebSocketProviderProps {
  children: ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const [pipelineData, setPipelineData] = useState<PipelineData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    // Connect to Flask backend
    const socket = io('http://localhost:5001', {
      transports: ['websocket'],
    });

    socketRef.current = socket;

    socket.on('connect', () => {
      console.log('Connected to WebSocket server');
      setIsConnected(true);
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
      setIsConnected(false);
    });

    socket.on('pipeline_update', (data: PipelineData) => {
      console.log('Received pipeline update:', data);
      setPipelineData(data);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const switchBuild = (runId: string) => {
    if (socketRef.current) {
      socketRef.current.emit('switch_build', { runId });
    }
  };

  const requestUpdate = () => {
    if (socketRef.current) {
      socketRef.current.emit('request_update');
    }
  };

  return (
    <WebSocketContext.Provider value={{ pipelineData, isConnected, switchBuild, requestUpdate }}>
      {children}
    </WebSocketContext.Provider>
  );
};