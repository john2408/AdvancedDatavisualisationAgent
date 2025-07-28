import React from 'react';
import styled from 'styled-components';
import { FiCpu, FiMessageSquare, FiRefreshCw, FiTarget } from 'react-icons/fi';

const OrchestratorContainer = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 0.5rem;
  margin: 1rem 0;
  padding: 1.5rem;
  color: white;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
`;

const OrchestratorHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  
  h3 {
    margin: 0;
    font-size: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
`;

const IntentInfo = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const InfoCard = styled.div`
  background: rgba(255, 255, 255, 0.15);
  border-radius: 0.5rem;
  padding: 1rem;
  backdrop-filter: blur(10px);
  
  h4 {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    opacity: 0.8;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  p {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
  }
`;

const ConfidenceBar = styled.div`
  width: 100%;
  height: 0.5rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 0.25rem;
  overflow: hidden;
  margin-top: 0.5rem;
`;

const ConfidenceFill = styled.div`
  height: 100%;
  background: ${props => {
    if (props.confidence > 0.8) return '#10b981';
    if (props.confidence > 0.6) return '#f59e0b';
    return '#ef4444';
  }};
  width: ${props => props.confidence * 100}%;
  transition: width 0.5s ease;
`;

const ReasoningText = styled.div`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-top: 1rem;
  font-style: italic;
  line-height: 1.5;
`;

const ConversationContext = styled.div`
  margin-top: 1rem;
  
  h4 {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    opacity: 0.8;
  }
  
  ul {
    margin: 0;
    padding-left: 1.5rem;
    
    li {
      margin-bottom: 0.25rem;
      font-size: 0.9rem;
    }
  }
`;

const OrchestrationFlow = ({ 
  actionType, 
  confidence, 
  reasoning, 
  conversationHistory, 
  currentDataContext,
  isVisible = true 
}) => {
  if (!isVisible || !actionType) return null;

  const getActionTypeColor = (type) => {
    switch (type?.toLowerCase()) {
      case 'new_query': return '#3b82f6';
      case 'follow_up': return '#10b981';
      case 'data_question': return '#f59e0b';
      case 'visualization_change': return '#8b5cf6';
      default: return '#6b7280';
    }
  };

  const getActionTypeIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'new_query': return <FiTarget />;
      case 'follow_up': return <FiMessageSquare />;
      case 'data_question': return <FiCpu />;
      case 'visualization_change': return <FiRefreshCw />;
      default: return <FiCpu />;
    }
  };

  const getActionTypeDescription = (type) => {
    switch (type?.toLowerCase()) {
      case 'new_query': 
        return 'Starting fresh analysis with new data request';
      case 'follow_up': 
        return 'Building on existing data and context';
      case 'data_question': 
        return 'Answering questions about current visualization';
      case 'visualization_change': 
        return 'Modifying current chart or creating alternative view';
      default: 
        return 'Processing your request';
    }
  };

  const hasContext = currentDataContext && Object.keys(currentDataContext).length > 0;
  const recentMessages = conversationHistory ? conversationHistory.slice(-3) : [];

  return (
    <OrchestratorContainer>
      <OrchestratorHeader>
        <h3>
          <FiCpu />
          Intent Orchestration Engine
        </h3>
      </OrchestratorHeader>
      
      <IntentInfo>
        <InfoCard>
          <h4>
            {getActionTypeIcon(actionType)}
            Action Type
          </h4>
          <p style={{ color: getActionTypeColor(actionType) }}>
            {actionType?.toUpperCase()}
          </p>
        </InfoCard>
        
        <InfoCard>
          <h4>
            <FiTarget />
            Confidence Level
          </h4>
          <p>{Math.round((confidence || 0) * 100)}%</p>
          <ConfidenceBar>
            <ConfidenceFill confidence={confidence || 0} />
          </ConfidenceBar>
        </InfoCard>
        
        <InfoCard>
          <h4>
            <FiCpu />
            Processing Mode
          </h4>
          <p>{getActionTypeDescription(actionType)}</p>
        </InfoCard>
      </IntentInfo>
      
      {reasoning && (
        <ReasoningText>
          <strong>🎯 Reasoning:</strong> {reasoning}
        </ReasoningText>
      )}
      
      <ConversationContext>
        <h4>📊 Context Awareness</h4>
        <ul>
          <li>
            <strong>Data Context:</strong> {hasContext ? '✅ Available' : '❌ None'}
          </li>
          <li>
            <strong>Conversation History:</strong> {recentMessages.length} recent messages
          </li>
          <li>
            <strong>Memory State:</strong> {actionType === 'follow_up' ? '🧠 Active' : '🔄 Fresh'}
          </li>
          <li>
            <strong>Pipeline Route:</strong> {
              actionType === 'new_query' ? '🚀 Full Pipeline' : 
              actionType === 'follow_up' ? '⚡ Fast Track' : 
              '🎨 Specialized Handler'
            }
          </li>
        </ul>
      </ConversationContext>
    </OrchestratorContainer>
  );
};

export default OrchestrationFlow;
