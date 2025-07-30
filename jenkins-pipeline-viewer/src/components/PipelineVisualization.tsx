import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, Circle, PlayCircle, Loader, Clock, AlertCircle } from 'lucide-react';
import { useWebSocket } from '../contexts/WebSocketContext';
import BuildSelector from './BuildSelector';
import RunInfo from './RunInfo';
import './PipelineVisualization.css';

const PipelineVisualization: React.FC = () => {
  const { pipelineData, isConnected } = useWebSocket();

  const getStageIcon = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'SUCCESS':
        return <CheckCircle className="stage-icon success" />;
      case 'FAILURE':
      case 'FAILED':
        return <XCircle className="stage-icon failure" />;
      case 'IN_PROGRESS':
      case 'RUNNING':
        return <Loader className="stage-icon in-progress spinning" />;
      case 'PAUSED':
        return <Clock className="stage-icon paused" />;
      case 'UNSTABLE':
        return <AlertCircle className="stage-icon unstable" />;
      case 'NOT_EXECUTED':
      case 'NOT_BUILT':
        return <Circle className="stage-icon not-executed" />;
      default:
        return <PlayCircle className="stage-icon" />;
    }
  };

  const getStageStatusClass = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'SUCCESS':
        return 'stage-success';
      case 'FAILURE':
      case 'FAILED':
        return 'stage-failure';
      case 'IN_PROGRESS':
      case 'RUNNING':
        return 'stage-in-progress';
      case 'PAUSED':
        return 'stage-paused';
      case 'UNSTABLE':
        return 'stage-unstable';
      default:
        return 'stage-not-executed';
    }
  };

  const formatDuration = (millis: number) => {
    if (!millis) return '';
    const seconds = Math.floor(millis / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`;
    }
    return `${seconds}s`;
  };

  if (!isConnected) {
    return (
      <div className="pipeline-container">
        <div className="connection-status">
          <Loader className="spinning" />
          <span>Connecting to Jenkins...</span>
        </div>
      </div>
    );
  }

  if (!pipelineData) {
    return (
      <div className="pipeline-container">
        <div className="connection-status">
          <span>Waiting for pipeline data...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="pipeline-container">
      <div className="pipeline-header">
        <h1>Jenkins Pipeline Monitor</h1>
        <BuildSelector />
      </div>

      <RunInfo runInfo={pipelineData.runInfo} />

      <div className="pipeline-stages">
        <div className="stages-header">
          <span className="start-marker">Start</span>
          <div className="pipeline-line" />
        </div>

        <div className="stages-flow">
          {pipelineData.stages.map((stage, index) => (
            <motion.div
              key={`${stage.name}-${index}`}
              className={`stage-container ${getStageStatusClass(stage.status)}`}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className="stage-icon-container">
                {getStageIcon(stage.status)}
              </div>
              
              <div className="stage-content">
                <h3 className="stage-name">{stage.name}</h3>
                {stage.durationMillis && (
                  <span className="stage-duration">{formatDuration(stage.durationMillis)}</span>
                )}
              </div>

              {stage.stageFlowNodes && stage.stageFlowNodes.length > 0 && (
                <motion.div 
                  className="stage-steps"
                  initial={{ height: 0 }}
                  animate={{ height: 'auto' }}
                  transition={{ duration: 0.3 }}
                >
                  {stage.stageFlowNodes.map((step, stepIndex) => (
                    <div 
                      key={`${step.name}-${stepIndex}`} 
                      className={`step ${step.status?.toLowerCase()}`}
                    >
                      <span className="step-name">{step.name}</span>
                      {step.parameterDescription && (
                        <span className="step-description">{step.parameterDescription}</span>
                      )}
                    </div>
                  ))}
                </motion.div>
              )}

              {index < pipelineData.stages.length - 1 && (
                <div className="stage-connector" />
              )}
            </motion.div>
          ))}
        </div>

        <div className="stages-footer">
          <div className="pipeline-line" />
          <span className="end-marker">End</span>
        </div>
      </div>
    </div>
  );
};

export default PipelineVisualization;