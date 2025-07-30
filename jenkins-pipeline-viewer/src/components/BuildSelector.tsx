import React from 'react';
import { useWebSocket } from '../contexts/WebSocketContext';
import { RefreshCw } from 'lucide-react';

const BuildSelector: React.FC = () => {
  const { pipelineData, switchBuild, requestUpdate } = useWebSocket();

  if (!pipelineData) return null;

  const currentRunId = pipelineData.runInfo?.id;
  const recentRuns = pipelineData.recentRuns || [];

  return (
    <div className="build-selector">
      <select 
        value={currentRunId} 
        onChange={(e) => switchBuild(e.target.value)}
        className="build-select"
      >
        {recentRuns.map((run) => (
          <option key={run.id} value={run.id}>
            #{run.name} - {run.status}
          </option>
        ))}
      </select>
      
      <button 
        onClick={requestUpdate}
        className="refresh-button"
        title="Refresh pipeline data"
      >
        <RefreshCw size={16} />
      </button>
    </div>
  );
};

export default BuildSelector;