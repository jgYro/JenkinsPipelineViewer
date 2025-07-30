import React from 'react';
import { Calendar, Clock, User } from 'lucide-react';

interface RunInfoProps {
  runInfo: {
    id: string;
    name: string;
    status: string;
    startTimeMillis: number;
    durationMillis: number;
    queueDurationMillis: number;
    causesString: string;
  };
}

const RunInfo: React.FC<RunInfoProps> = ({ runInfo }) => {
  const formatTime = (millis: number) => {
    return new Date(millis).toLocaleString();
  };

  const formatDuration = (millis: number) => {
    if (!millis) return '0s';
    const seconds = Math.floor(millis / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    }
    return `${seconds}s`;
  };

  const getStatusClass = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'SUCCESS':
        return 'status-success';
      case 'FAILURE':
      case 'FAILED':
        return 'status-failure';
      case 'IN_PROGRESS':
      case 'RUNNING':
        return 'status-in-progress';
      case 'UNSTABLE':
        return 'status-unstable';
      default:
        return 'status-unknown';
    }
  };

  return (
    <div className="run-info">
      <div className="run-info-header">
        <h2>Build #{runInfo.name}</h2>
        <span className={`run-status ${getStatusClass(runInfo.status)}`}>
          {runInfo.status}
        </span>
      </div>
      
      <div className="run-info-details">
        <div className="info-item">
          <Calendar size={16} />
          <span>Started: {formatTime(runInfo.startTimeMillis)}</span>
        </div>
        
        <div className="info-item">
          <Clock size={16} />
          <span>Duration: {formatDuration(runInfo.durationMillis)}</span>
        </div>
        
        {runInfo.queueDurationMillis > 0 && (
          <div className="info-item">
            <Clock size={16} />
            <span>Queue time: {formatDuration(runInfo.queueDurationMillis)}</span>
          </div>
        )}
        
        <div className="info-item">
          <User size={16} />
          <span>Triggered by: {runInfo.causesString}</span>
        </div>
      </div>
    </div>
  );
};

export default RunInfo;