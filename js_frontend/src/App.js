import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

import {
  SidebarHeader,
  Message,
  Input,
  MetricCard,
  WelcomeContainer,
  FollowUpContainer, 
  PlotlyChartContainer
} from './styles/enhancedComponents';
import { FiSend, FiMic, FiBarChart } from 'react-icons/fi';
import { agentAPI } from './api';
import PipelineSteps from './components/PipelineSteps';
import PlotlyVisualizationComp from './components/PlotlyVisualization';
import OrchestrationFlow from './components/OrchestrationFlow';
import DatabaseSchemaViewer from './components/DatabaseSchemaViewer';
import { generateAndReviewSQL } from './utils/sqlRetrieval';
import { executeSQLQuery } from './utils/executeSQL';
import { performDataAnalysis } from './utils/performDataAnalysis';
import { performVisualizationGeneration, createAlternativeVisualization } from './utils/performVisualizationGeneration';
import { DataTable } from './utils/renderDataTable';
import {
  ResponsiveContainer,
  ResponsiveSidebar,
  ResponsiveMainPanel,
  ResponsiveMetricsGrid,
  ResponsiveWelcomeButtons,
  ResponsiveFollowUpGrid,
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
} from './styles/ResponsiveLayout';



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

      // Create callbacks object for modular functions
      const callbacks = {
        updatePipelineStep,
        completePipelineStep,
        addMessage,
        setCurrentData  // This ensures executeSQL can set currentData directly
      };

      // Steps 1 & 2: Generate and Review SQL
      const sqlResult = await generateAndReviewSQL(userMessage, dbSchemaForAgent, callbacks);
      
      if (!sqlResult.success) {
        throw new Error(`SQL generation/review failed: ${sqlResult.error}`);
      }

      // Step 3: Execute SQL Query
      const executionResult = await executeSQLQuery(sqlResult.data.reviewedSQL, callbacks);
      
      if (!executionResult.success) {
        throw new Error(`SQL execution failed: ${executionResult.error}`);
      }

      // currentData is already set by executeSQLQuery callback
      // Confirm data is available for table rendering
      const queryData = executionResult.data.queryData;
      addMessage('assistant', `📊 Table data is ready! ${queryData.length} rows available for display.`);

      // Step 4a: Data Analysis
      updatePipelineStep('data_analysis');
      let analysisResult;
      try {
        analysisResult = await performDataAnalysis(queryData, userMessage, { addMessage });
        if (!analysisResult.success) {
          completePipelineStep('data_analysis');
          addMessage('assistant', '⚠️ Data analysis failed, but table is ready.');
          return;
        }
      } catch (err) {
        completePipelineStep('data_analysis');
        addMessage('assistant', '⚠️ Data analysis failed, but table is ready.');
        return;
      }

      // Step 4b: Visualization Generation
      let vizResult;
      try {
        vizResult = await performVisualizationGeneration(
          queryData,
          userMessage,
          analysisResult.data,
          { addMessage, setCurrentVisualization, setFollowUpQuestions }
        );
        
        // Debug: Log the visualization result
        console.log('🐛 VISUALIZATION RESULT:', vizResult);
        
        if (vizResult.success) {
          // Visualization is already set by the callback in performVisualizationGeneration
          completePipelineStep('data_analysis');
          if (vizResult.fallbackCreated) {
            addMessage('assistant', '🎉 Complete! Table and fallback visualization are ready.');
          } else {
            addMessage('assistant', '🎉 Complete! Both table and visualization are ready.');
          }
        } else {
          // No visualization could be created
          setCurrentVisualization(null);
          completePipelineStep('data_analysis');
          addMessage('assistant', '⚠️ Table ready! Visualization failed but your data is displayed in the table above.');
        }
      } catch (vizError) {
        // Optionally create a fallback visualization here
        setCurrentVisualization(null);
        completePipelineStep('data_analysis');
        addMessage('assistant', '📊 Table ready! Visualization failed but your query results are displayed above.');
      }

    } catch (error) {
      console.error('Error in new query pipeline:', error);
      addMessage('assistant', `❌ PIPELINE ERROR: ${error.message}\n\nPlease check the console for detailed error information.`);
      resetPipelineState();
    }
  };

  const handleFollowUpQuestion = async (userMessage) => {
    try {
      const callbacks = {
        addMessage,
        setCurrentVisualization
      };

      if (userMessage.toLowerCase().includes('convert') || 
          userMessage.toLowerCase().includes('change to') ||
          userMessage.toLowerCase().includes('show as')) {
        // Handle visualization conversion using modular function
        const altVizResult = await createAlternativeVisualization(
          userMessage,
          currentData,
          currentVisualization?.type || 'bar',
          callbacks
        );

        if (!altVizResult.success) {
          throw new Error(`Alternative visualization failed: ${altVizResult.error}`);
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

        if (!answerResult.success) {
          throw new Error(`Data question analysis failed: ${answerResult.error || 'Unknown error'}`);
        }

        addMessage('assistant', answerResult.data.answer);
      }
    } catch (error) {
      console.error('Error in follow-up flow:', error);
      addMessage('assistant', `❌ FOLLOW-UP ERROR: ${error.message}\n\nPlease check the console for detailed error information.`);
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

  // Test function to simulate backend visualization response
  const testBackendVisualization = () => {
    const backendFormat = {
      "type": "bar",
      "data": {
        "x": ["AUDI", "BMW", "MERCEDES-BENZ"],
        "y": [120, 150, 100]
      },
      "layout": {
        "title": "Test: Vehicles by Manufacturer",
        "xaxis": {"title": "manufacturer"},
        "yaxis": {"title": "count"},
        "barmode": "group",
        "showlegend": false,
        "plot_bgcolor": "white",
        "paper_bgcolor": "white",
        "font": {"color": "#2E2E2E", "family": "Arial, sans-serif"}
      }
    };
    
    console.log('🧪 Testing backend format:', backendFormat);
    setCurrentVisualization(backendFormat);
    addMessage('assistant', '🧪 Test visualization loaded with backend format');
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
        
        {/* Show Data Results Section - Independent of Visualization */}
        {currentData && currentData.length > 0 && (
          <>
            {/* Debug info - simplified */}
            <div style={{ background: '#f0f9ff', padding: '0.75rem', margin: '1rem 0', border: '1px solid #0ea5e9', fontSize: '0.85rem' }}>
              <strong>🐛 DEBUG:</strong> {currentData.length} rows loaded, keys: {currentData[0] ? Object.keys(currentData[0]).join(', ') : 'N/A'}
            </div>
            
            {/* Metrics Overview */}
            {renderMetrics()}
            
            {/* Data Table - Always show when we have data */}
            <ResponsiveCard style={{ marginTop: '1rem' }}>
              <div style={{ padding: '1rem', borderBottom: '1px solid #e2e8f0', backgroundColor: '#f8fafc' }}>
                <h3 style={{ margin: 0 }}>📊 Query Results ({currentData.length} rows)</h3>
              </div>
              <DataTable 
                data={currentData} 
                options={{ 
                  title: 'Query Results',
                  maxRows: 100,
                  showRowNumbers: false
                }}
              />
            </ResponsiveCard>
          </>
        )}
  
        
        {/* Show Visualization Section - Only when currentVisualization is available */}
        {currentVisualization && (
          <PlotlyChartContainer>
            <PlotlyVisualizationComp
              plotSpec={currentVisualization}
              title={currentVisualization?.layout?.title || 'Visualization'}
              isLoading={isLoading}
              useResizeHandler={true}
              style={{ width: '100%', height: '100%' }}
            />
          </PlotlyChartContainer>
        )}
        
        {/* Show error message if visualization fails */}
        {!currentVisualization && currentData && currentData.length > 0 && !isLoading && (
          <div style={{ color: '#d97706', background: '#fef3c7', border: '1px solid #f59e0b', padding: '1rem', borderRadius: '0.5rem', margin: '1rem 0', textAlign: 'center' }}>
            <strong>⚠️ Visualization not available:</strong> Data is loaded but no chart could be generated. Check the console for details.
          </div>
        )}
        

        {/* Follow-up Questions - Show when available */}
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

        {/* Welcome Screen - Only show when no data */}
        {(!currentData || currentData.length === 0) && (
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
