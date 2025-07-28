import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FiSend, FiMic, FiBarChart } from 'react-icons/fi';
import { agentAPI } from './api';
import PipelineSteps from './components/PipelineSteps';
import PlotlyVisualization from './components/PlotlyVisualization';
import OrchestrationFlow from './components/OrchestrationFlow';
import DatabaseSchemaViewer from './components/DatabaseSchemaViewer';
import {
  ResponsiveContainer,
  ResponsiveSidebar,
  ResponsiveMainPanel,
  ResponsiveMetricsGrid,
  ResponsiveWelcomeButtons,
  ResponsiveFollowUpGrid,
  ResponsiveTableContainer,
  ResponsiveChatContainer,
  ResponsiveInputContainer,
  ResponsiveInputWrapper,
  ResponsiveHeading,
  ResponsiveSubheading,
  ResponsiveText,
  ResponsiveCard,
  ResponsiveButton,
  ResponsiveFollowUpButton,
  ResponsiveLoadingSpinner,
  media
} from './styles/ResponsiveLayout';

// Enhanced Styled Components for remaining elements
const SidebarHeader = styled.div`
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  
  h1 {
    margin: 0 0 0.5rem 0;
    font-size: 1.5rem;
    color: #1f2937;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    
    ${media.mobile} {
      font-size: 1.25rem;
    }
  }
  
  p {
    margin: 0;
    color: #6b7280;
    font-size: 0.9rem;
    
    ${media.mobile} {
      font-size: 0.8rem;
    }
  }
`;

const Message = styled.div`
  margin-bottom: 1rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  max-width: 85%;
  word-wrap: break-word;
  
  ${props => props.isUser ? `
    background-color: #3b82f6;
    color: white;
    margin-left: auto;
    text-align: right;
  ` : `
    background-color: #f1f5f9;
    color: #1f2937;
    border: 1px solid #e2e8f0;
  `}
  
  ${media.mobile} {
    max-width: 95%;
    padding: 0.5rem;
    font-size: 0.9rem;
  }
`;

const Input = styled.input`
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #000000;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  outline: none;
  
  &:focus {
    border-color: #3b82f6;
  }
  
  ${media.mobile} {
    width: 100%;
    margin-bottom: 0.5rem;
  }
`;

const MetricCard = styled(ResponsiveCard)`
  h3 {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    
    ${media.mobile} {
      font-size: 0.8rem;
    }
  }
  
  p {
    margin: 0;
    font-size: 1.5rem;
    font-weight: bold;
    color: #1f2937;
    
    ${media.mobile} {
      font-size: 1.25rem;
    }
  }
`;

const WelcomeContainer = styled.div`
  text-align: center;
  padding: 3rem 2rem;
  
  ${media.mobile} {
    padding: 2rem 1rem;
  }
`;

const FollowUpContainer = styled.div`
  margin-top: 2rem;
  
  h3 {
    color: #1f2937;
    margin-bottom: 1rem;
    
    ${media.mobile} {
      font-size: 1.1rem;
    }
  }
`;

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! I'm your Visualization Assistant. I can generate SQL queries and create visualizations from your database.",
      time: new Date().toLocaleTimeString()
    }
  ]);
  
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentVisualization, setCurrentVisualization] = useState(null);
  const [currentData, setCurrentData] = useState(null);
  const [followUpQuestions, setFollowUpQuestions] = useState([]);
  const [apiStatus, setApiStatus] = useState('checking');
  
  // Database schema state
  const [dbSchema, setDbSchema] = useState({
    agent: '',
    user: '',
    path: ''
  });
  const [schemaLoaded, setSchemaLoaded] = useState(false);
  
  // Pipeline state management
  const [currentStep, setCurrentStep] = useState(null);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [orchestrationData, setOrchestrationData] = useState(null);
  const [pipelineVisible, setPipelineVisible] = useState(false);

  // Check API health and load schema on component mount
  useEffect(() => {
    checkAPIHealth();
    loadDatabaseSchema();
  }, []);

  const checkAPIHealth = async () => {
    try {
      await agentAPI.healthCheck();
      setApiStatus('connected');
    } catch (error) {
      setApiStatus('disconnected');
      console.error('API connection failed:', error);
    }
  };

  const loadDatabaseSchema = async () => {
    try {
      const schemaData = await agentAPI.getDatabaseSchema();
      setDbSchema({
        agent: schemaData.db_schema_agent || '',
        user: schemaData.db_schema_user || '',
        path: schemaData.db_path || ''
      });
      setSchemaLoaded(true);
    } catch (error) {
      console.error('Failed to load database schema:', error);
      // Set fallback schema
      setDbSchema({
        agent: `
          Tables: vehicles, manufacturers, registrations, regions, time_periods
          Key relationships: 
          - vehicles.manufacturer_id -> manufacturers.id
          - registrations.vehicle_id -> vehicles.id
          - registrations.region_id -> regions.id
          - registrations.time_period_id -> time_periods.id
        `,
        user: 'Vehicle registration database with manufacturers, vehicle types, and regional data.',
        path: 'data/registered_vehicles.sqlite'
      });
      setSchemaLoaded(true);
    }
  };

  const addMessage = (role, content) => {
    const newMessage = {
      role,
      content,
      time: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const resetPipelineState = () => {
    setCurrentStep(null);
    setCompletedSteps([]);
    setPipelineVisible(false);
    setOrchestrationData(null);
  };

  const updatePipelineStep = (stepId) => {
    setCurrentStep(stepId);
    setPipelineVisible(true);
  };

  const completePipelineStep = (stepId) => {
    setCompletedSteps(prev => [...prev, stepId]);
    setCurrentStep(null);
  };

  const createFallbackVisualization = (data) => {
    const keys = Object.keys(data[0] || {});
    const numericKey = keys.find(key => typeof data[0][key] === 'number');
    const categoryKey = keys.find(key => typeof data[0][key] === 'string');
    
    return {
      type: 'bar',
      data: {
        x: data.map(d => d[categoryKey]),
        y: data.map(d => d[numericKey])
      },
      layout: {
        title: 'Data Overview',
        xaxis: { title: categoryKey || 'Category' },
        yaxis: { title: numericKey || 'Value' }
      }
    };
  };

  const performDataAnalysisAndVisualization = async (data, userMessage, dbSchema) => {
    try {
      // Step 4a: Analyze data
      addMessage('assistant', '📊 Analyzing data patterns...');
      
      const analysisResult = await agentAPI.analyzeData(
        Object.keys(data[0] || {}).join(', '),
        `${data.length} rows × ${Object.keys(data[0] || {}).length} columns`,
        JSON.stringify(Object.keys(data[0] || {}).reduce((acc, key) => ({ ...acc, [key]: 'string' }), {})),
        JSON.stringify(data.slice(0, 3)),
        userMessage
      );

      if (analysisResult.success) {
        // Step 4b: Create visualization
        addMessage('assistant', '🎨 Creating visualization...');
        
        const vizResult = await agentAPI.createVisualization(
          JSON.stringify(data),
          userMessage,
          analysisResult.data.recommended_visualizations.join(', '),
          analysisResult.data.analysis,
          analysisResult.data.key_findings
        );

        if (vizResult.success) {
          // Convert backend visualization format to Plotly format
          const plotSpec = JSON.parse(vizResult.data.plot_spec);
          
          // Ensure the plot has proper structure for PlotlyVisualization component
          const processedViz = {
            data: Array.isArray(plotSpec.data) ? plotSpec.data : [plotSpec.data],
            layout: plotSpec.layout || {
              title: vizResult.data.title || 'Data Visualization',
              plot_bgcolor: 'white',
              paper_bgcolor: 'white',
              font: { color: 'black' }
            },
            type: vizResult.data.plot_type || 'bar'
          };
          
          setCurrentVisualization(processedViz);
          addMessage('assistant', '✨ Visualization created successfully!');

          // Generate follow-up questions
          const followUpResult = await agentAPI.generateFollowUpQuestions(
            analysisResult.data.analysis,
            userMessage,
            analysisResult.data.key_findings.join(', '),
            dbSchema.agent
          );

          if (followUpResult.success) {
            setFollowUpQuestions(followUpResult.data.questions);
          }
        }
      }

    } catch (error) {
      console.error('Error in data analysis:', error);
      addMessage('assistant', 'Created basic visualization due to analysis error.');
      
      // Fallback to simple visualization
      const fallbackViz = createFallbackVisualization(data);
      setCurrentVisualization(fallbackViz);
    }
  };

  const handleNewQueryPipeline = async (userMessage) => {
    try {
      // Use loaded database schema
      const dbSchemaForAgent = dbSchema.agent || `
        Tables: vehicles, manufacturers, registrations, regions, time_periods
        Key relationships: 
        - vehicles.manufacturer_id -> manufacturers.id
        - registrations.vehicle_id -> vehicles.id
        - registrations.region_id -> regions.id
        - registrations.time_period_id -> time_periods.id
      `;

      // Step 1: Generate SQL
      updatePipelineStep('sql_generation');
      addMessage('assistant', '🤖 Generating SQL query...');
      
      const sqlResult = await agentAPI.generateSQL(userMessage, dbSchemaForAgent);
      
      if (!sqlResult.success) {
        throw new Error('SQL generation failed');
      }

      const initialSQL = sqlResult.data.sqlquery;
      completePipelineStep('sql_generation');
      addMessage('assistant', `📝 Generated SQL Query`);
      
      // Step 2: Review SQL
      updatePipelineStep('sql_review');
      addMessage('assistant', '🔍 Reviewing SQL with GPT-4o verifier...');
      
      const reviewResult = await agentAPI.reviewSQL(initialSQL, dbSchemaForAgent);
      
      if (!reviewResult.success) {
        throw new Error('SQL review failed');
      }

      const reviewedSQL = reviewResult.data.reviewed_sqlquery;
      const wasChanged = initialSQL.trim() !== reviewedSQL.trim();
      
      completePipelineStep('sql_review');
      
      if (wasChanged) {
        addMessage('assistant', '✅ SQL optimized and improved');
      } else {
        addMessage('assistant', '✅ SQL validated - no changes needed');
      }

      // Step 3: Execute Query
      updatePipelineStep('query_execution');
      addMessage('assistant', '🔄 Executing SQL query...');
      
      // Execute SQL query against the database
      const executionResult = await agentAPI.executeSQL(reviewedSQL);
      
      if (!executionResult.success) {
        throw new Error('SQL execution failed');
      }

      const queryData = executionResult.data.results;
      const metadata = executionResult.data.metadata;
      
      setCurrentData(queryData);
      completePipelineStep('query_execution');
      addMessage('assistant', `✅ Retrieved ${metadata.row_count} rows successfully`);

      // Step 4: Data Analysis & Visualization
      updatePipelineStep('data_analysis');
      await performDataAnalysisAndVisualization(queryData, userMessage, dbSchemaForAgent);
      
      completePipelineStep('data_analysis');

    } catch (error) {
      console.error('Error in new query pipeline:', error);
      addMessage('assistant', 'Sorry, I encountered an error processing your query.');
      resetPipelineState();
    }
  };

  const handleFollowUpQuestion = async (userMessage) => {
    try {
      if (userMessage.toLowerCase().includes('convert') || 
          userMessage.toLowerCase().includes('change to') ||
          userMessage.toLowerCase().includes('show as')) {
        // Handle visualization conversion
        addMessage('assistant', '🎨 Creating alternative visualization...');
        const altVizResult = await agentAPI.createAlternativeVisualization(
          userMessage,
          JSON.stringify(currentData),
          currentVisualization?.type || 'bar'
        );

        if (altVizResult.success) {
          // Convert backend visualization format to Plotly format
          const plotSpec = JSON.parse(altVizResult.data.plot_spec);
          
          const processedViz = {
            data: Array.isArray(plotSpec.data) ? plotSpec.data : [plotSpec.data],
            layout: plotSpec.layout || {
              title: altVizResult.data.title || 'Alternative Visualization',
              plot_bgcolor: 'white',
              paper_bgcolor: 'white',
              font: { color: 'black' }
            },
            type: altVizResult.data.plot_type || 'bar'
          };
          
          setCurrentVisualization(processedViz);
          addMessage('assistant', '✨ Alternative visualization created!');
        }
      } else {
        // Handle data question
        addMessage('assistant', '🔍 Analyzing current data to answer your question...');
        const answerResult = await agentAPI.answerDataQuestion(
          userMessage,
          JSON.stringify(currentData),
          'Current data summary',
          JSON.stringify({ type: currentVisualization?.type || 'unknown' })
        );

        if (answerResult.success) {
          addMessage('assistant', answerResult.data.answer);
        }
      }
    } catch (error) {
      console.error('Error in follow-up flow:', error);
      addMessage('assistant', 'Sorry, I encountered an error with your follow-up question.');
    }
  };

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;
    
    const userMessage = inputValue;
    setInputValue('');
    addMessage('user', userMessage);
    setIsLoading(true);
    resetPipelineState();

    try {
      // Step 0: Orchestrate intent (Enhanced Pipeline Architecture)
      updatePipelineStep('orchestration');
      addMessage('assistant', '🧠 Understanding your intent...');
      
      const orchestrationResult = await agentAPI.orchestrateIntent(
        userMessage,
        JSON.stringify(messages.slice(-5)),
        JSON.stringify(currentData || {})
      );

      if (orchestrationResult.success) {
        const { action_type, confidence, reasoning } = orchestrationResult.data;
        
        // Store orchestration data for UI
        setOrchestrationData({
          actionType: action_type,
          confidence: confidence,
          reasoning: reasoning,
          conversationHistory: messages.slice(-5),
          currentDataContext: currentData || {}
        });
        
        completePipelineStep('orchestration');
        addMessage('assistant', `🎯 Intent: ${action_type.toUpperCase()} (Confidence: ${Math.round(confidence * 100)}%)`);

        if (action_type === 'follow_up' && currentData) {
          // Handle follow-up question with existing data
          await handleFollowUpQuestion(userMessage);
        } else {
          // Handle new query with full pipeline
          await handleNewQueryPipeline(userMessage);
        }
      }
    } catch (error) {
      console.error('Error processing request:', error);
      addMessage('assistant', 'Sorry, I encountered an error processing your request. Please make sure the backend server is running.');
      resetPipelineState();
    } finally {
      setIsLoading(false);
    }
  };

  const handleFollowUpClick = (question) => {
    setInputValue(question);
  };

  const renderDataTable = () => {
    if (!currentData || currentData.length === 0) return null;

    return (
      <ResponsiveTableContainer>
        <table>
          <thead>
            <tr>
              {Object.keys(currentData[0] || {}).map(key => (
                <th key={key}>{key.replace(/_/g, ' ').toUpperCase()}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentData.map((row, index) => (
              <tr key={index}>
                {Object.values(row).map((value, i) => (
                  <td key={i}>
                    {typeof value === 'number' ? 
                      (value % 1 === 0 ? value.toLocaleString() : value.toFixed(2)) : 
                      value
                    }
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </ResponsiveTableContainer>
    );
  };

  const renderMetrics = () => {
    if (!currentData || currentData.length === 0) return null;

    const numericColumns = Object.keys(currentData[0]).filter(key => 
      typeof currentData[0][key] === 'number'
    );
    
    const totalRecords = currentData.length;
    const topValue = numericColumns.length > 0 ? 
      Math.max(...currentData.map(d => d[numericColumns[0]])) : 0;
    const avgValue = numericColumns.length > 0 ? 
      (currentData.reduce((sum, d) => sum + d[numericColumns[0]], 0) / currentData.length).toFixed(1) : 0;

    return (
      <ResponsiveMetricsGrid>
        <MetricCard>
          <h3>Total Records</h3>
          <p>{totalRecords.toLocaleString()}</p>
        </MetricCard>
        <MetricCard>
          <h3>Peak Value</h3>
          <p>{topValue.toLocaleString()}</p>
        </MetricCard>
        <MetricCard>
          <h3>Average</h3>
          <p>{avgValue}</p>
        </MetricCard>
      </ResponsiveMetricsGrid>
    );
  };

  return (
    <ResponsiveContainer>
      <ResponsiveSidebar>
        <SidebarHeader>
          <h1>
            <FiBarChart />
            Visualization Agent
          </h1>
          <p>AI-powered SQL generation and visualization</p>
          <div style={{ marginTop: '0.5rem', fontSize: '0.8rem' }}>
            API Status: <span style={{ color: apiStatus === 'connected' ? '#10b981' : '#ef4444' }}>
              {apiStatus === 'connected' ? '🟢 Connected' : '🔴 Disconnected'}
            </span>
          </div>
        </SidebarHeader>
        
        <ResponsiveChatContainer>
          {messages.map((message, index) => (
            <Message key={index} isUser={message.role === 'user'}>
              {message.content}
            </Message>
          ))}
          {isLoading && (
            <ResponsiveLoadingSpinner>
              Processing your request...
            </ResponsiveLoadingSpinner>
          )}
        </ResponsiveChatContainer>
        
        <ResponsiveInputContainer>
          <ResponsiveInputWrapper>
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about your database..."
              disabled={isLoading}
            />
            <div>
              <ResponsiveButton variant="primary" onClick={handleSend} disabled={isLoading}>
                <FiSend />
              </ResponsiveButton>
              <ResponsiveButton>
                <FiMic />
              </ResponsiveButton>
            </div>
          </ResponsiveInputWrapper>
        </ResponsiveInputContainer>
      </ResponsiveSidebar>

      <ResponsiveMainPanel>
        <ResponsiveHeading>Ask questions about your data in natural language</ResponsiveHeading>
        <hr />
        
        {/* Show Orchestration Flow when active */}
        {orchestrationData && (
          <OrchestrationFlow
            actionType={orchestrationData.actionType}
            confidence={orchestrationData.confidence}
            reasoning={orchestrationData.reasoning}
            conversationHistory={orchestrationData.conversationHistory}
            currentDataContext={orchestrationData.currentDataContext}
            isVisible={true}
          />
        )}
        
        {/* Show Pipeline Steps when active */}
        {pipelineVisible && (
          <PipelineSteps
            currentStep={currentStep}
            completedSteps={completedSteps}
            confidence={orchestrationData?.confidence}
            actionType={orchestrationData?.actionType}
          />
        )}
        
        {currentVisualization ? (
          <>
            {/* Metrics Overview */}
            {renderMetrics()}
            
            {/* Data Table */}
            {renderDataTable()}
            
            {/* Main Visualization */}
            <PlotlyVisualization
              plotSpec={currentVisualization}
              title={currentVisualization?.layout?.title || 'Data Visualization'}
              isLoading={currentStep === 'data_analysis'}
            />
            
            {/* Follow-up Questions */}
            {followUpQuestions.length > 0 && (
              <FollowUpContainer>
                <h3>💡 Suggested follow-up questions:</h3>
                <ResponsiveFollowUpGrid>
                  {followUpQuestions.map((question, index) => (
                    <ResponsiveFollowUpButton
                      key={index}
                      onClick={() => handleFollowUpClick(question)}
                    >
                      {question}
                    </ResponsiveFollowUpButton>
                  ))}
                </ResponsiveFollowUpGrid>
              </FollowUpContainer>
            )}
          </>
        ) : (
          <WelcomeContainer>
            <ResponsiveSubheading>📊 Ready to Visualize Your Data</ResponsiveSubheading>
            <ResponsiveText>
              Ask questions about your vehicle registration data in the chat, and I'll create
              beautiful visualizations for you using AI-generated SQL queries and advanced pipeline architecture.
            </ResponsiveText>
            
            <DatabaseSchemaViewer 
              schema={dbSchema?.user || dbSchema?.agent || 'Loading schema...'} 
              isLoading={!schemaLoaded}
              title="📋 Database Schema"
            />
            
            <ResponsiveWelcomeButtons>
              <ResponsiveButton onClick={() => setInputValue("Which car manufacturers registered the most vehicles?")}>
                🏭 Top Manufacturers
              </ResponsiveButton>
              <ResponsiveButton onClick={() => setInputValue("How many electric vehicles were registered this year?")}>
                ⚡ Electric Vehicles
              </ResponsiveButton>
              <ResponsiveButton onClick={() => setInputValue("Show me monthly vehicle registration trends")}>
                📈 Monthly Trends
              </ResponsiveButton>
            </ResponsiveWelcomeButtons>
          </WelcomeContainer>
        )}
      </ResponsiveMainPanel>
    </ResponsiveContainer>
  );
}

export default App;
