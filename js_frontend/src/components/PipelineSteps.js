import React from 'react';
import styled from 'styled-components';
import { FiCpu, FiCode, FiSearch, FiPlay, FiBarChart, FiCheckCircle } from 'react-icons/fi';

const StepsContainer = styled.div`
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  margin: 1rem 0;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
`;

const StepsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const StepItem = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  transition: all 0.3s ease;
  
  ${props => {
    if (props.status === 'completed') return `
      background-color: #ecfdf5;
      border: 1px solid #10b981;
    `;
    if (props.status === 'active') return `
      background-color: #eff6ff;
      border: 1px solid #3b82f6;
      transform: scale(1.02);
    `;
    if (props.status === 'pending') return `
      background-color: #f9fafb;
      border: 1px solid #d1d5db;
    `;
    return `
      background-color: #f9fafb;
      border: 1px solid #d1d5db;
    `;
  }}
`;

const StepIcon = styled.div`
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  
  ${props => {
    if (props.status === 'completed') return `
      background-color: #10b981;
      color: white;
    `;
    if (props.status === 'active') return `
      background-color: #3b82f6;
      color: white;
    `;
    return `
      background-color: #6b7280;
      color: white;
    `;
  }}
`;

const StepContent = styled.div`
  flex: 1;
  
  h4 {
    margin: 0 0 0.25rem 0;
    color: #1f2937;
    font-size: 1rem;
  }
  
  p {
    margin: 0;
    color: #6b7280;
    font-size: 0.9rem;
  }
`;

const StepStatus = styled.div`
  font-size: 0.8rem;
  font-weight: 500;
  
  ${props => {
    if (props.status === 'completed') return `
      color: #10b981;
    `;
    if (props.status === 'active') return `
      color: #3b82f6;
    `;
    return `
      color: #6b7280;
    `;
  }}
`;

const LoadingDot = styled.div`
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background-color: #3b82f6;
  animation: pulse 1.5s ease-in-out infinite;
  
  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
`;

const PipelineSteps = ({ currentStep, completedSteps, confidence, actionType }) => {
  const steps = [
    {
      id: 'orchestration',
      icon: <FiCpu />,
      title: 'Intent Orchestration',
      description: 'Understanding your intent and routing your request'
    },
    {
      id: 'sql_generation',
      icon: <FiCode />,
      title: 'SQL Generation',
      description: 'Converting natural language to SQL query'
    },
    {
      id: 'sql_review',
      icon: <FiSearch />,
      title: 'SQL Review & Optimization',
      description: 'Reviewing and optimizing with GPT-4o'
    },
    {
      id: 'query_execution',
      icon: <FiPlay />,
      title: 'Query Execution',
      description: 'Executing SQL against the database'
    },
    {
      id: 'data_analysis',
      icon: <FiBarChart />,
      title: 'Data Analysis & Visualization',
      description: 'Analyzing patterns and creating visualizations'
    }
  ];

  const getStepStatus = (stepId) => {
    if (completedSteps.includes(stepId)) return 'completed';
    if (currentStep === stepId) return 'active';
    return 'pending';
  };

  return (
    <StepsContainer>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
        <h3 style={{ margin: 0, color: '#1f2937', fontSize: '1.1rem' }}>
          🏗️ Pipeline Architecture
        </h3>
        {actionType && (
          <div style={{ 
            padding: '0.25rem 0.75rem', 
            backgroundColor: '#fbbf24', 
            color: '#000', 
            borderRadius: '1rem', 
            fontSize: '0.8rem',
            fontWeight: 'bold'
          }}>
            {actionType.toUpperCase()} 
            {confidence && ` (${Math.round(confidence * 100)}%)`}
          </div>
        )}
      </div>
      
      <StepsList>
        {steps.map((step) => {
          const status = getStepStatus(step.id);
          return (
            <StepItem key={step.id} status={status}>
              <StepIcon status={status}>
                {status === 'completed' ? <FiCheckCircle /> : step.icon}
              </StepIcon>
              <StepContent>
                <h4>{step.title}</h4>
                <p>{step.description}</p>
              </StepContent>
              <StepStatus status={status}>
                {status === 'completed' && '✅ Complete'}
                {status === 'active' && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <LoadingDot />
                    Processing...
                  </div>
                )}
                {status === 'pending' && '⏳ Pending'}
              </StepStatus>
            </StepItem>
          );
        })}
      </StepsList>
    </StepsContainer>
  );
};

export default PipelineSteps;
