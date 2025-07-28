import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FiSend, FiMic, FiDatabase, FiBarChart3 } from 'react-icons/fi';
import Plot from 'react-plotly.js';
import { agentAPI } from './api';

// Styled Components
const AppContainer = styled.div`
  display: flex;
  height: 100vh;
  font-family: 'Arial', sans-serif;
  background-color: #f8fafc;
`;

const Sidebar = styled.div`
  width: 400px;
  background-color: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
`;

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
  }
  
  p {
    margin: 0;
    color: #6b7280;
    font-size: 0.9rem;
  }
`;

const ChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  overflow-y: auto;
  max-height: 350px;
`;

const Message = styled.div`
  margin-bottom: 1rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  max-width: 85%;
  
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
`;

const InputContainer = styled.div`
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
`;

const InputWrapper = styled.div`
  display: flex;
  gap: 0.5rem;
  align-items: center;
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
`;

const Button = styled.button`
  padding: 0.75rem;
  border: none;
  border-radius: 0.5rem;
  background-color: ${props => props.variant === 'primary' ? '#3b82f6' : '#6b7280'};
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  
  &:hover {
    background-color: ${props => props.variant === 'primary' ? '#2563eb' : '#4b5563'};
  }
  
  &:disabled {
    background-color: #9ca3af;
    cursor: not-allowed;
  }
`;

const MainPanel = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 2rem;
  overflow-y: auto;
`;

const WelcomeContainer = styled.div`
  text-align: center;
  padding: 3rem 2rem;
  
  h2 {
    color: #1f2937;
    margin-bottom: 1rem;
    font-size: 2rem;
  }
  
  p {
    color: #6b7280;
    font-size: 1.1rem;
    max-width: 600px;
    margin: 0 auto 2rem auto;
    line-height: 1.6;
  }
`;

const MetricsContainer = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
`;

const MetricCard = styled.div`
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  flex: 1;
  
  h3 {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  p {
    margin: 0;
    font-size: 1.5rem;
    font-weight: bold;
    color: #1f2937;
  }
`;

const SQLCodeBlock = styled.div`
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 0.25rem;
  padding: 1rem;
  margin: 1rem 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  
  pre {
    margin: 0;
    color: black;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 14px;
    line-height: 1.4;
    white-space: pre-wrap;
  }
`;

const DataTable = styled.div`
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  margin: 1rem 0;
  overflow-x: auto;
  
  table {
    width: 100%;
    border-collapse: collapse;
    
    th, td {
      padding: 0.75rem;
      text-align: left;
      border-bottom: 1px solid #e2e8f0;
    }
    
    th {
      background-color: #f8fafc;
      font-weight: bold;
      color: #1f2937;
    }
    
    td {
      color: #4b5563;
    }
  }
`;

const FollowUpContainer = styled.div`
  margin-top: 2rem;
  
  h3 {
    color: #1f2937;
    margin-bottom: 1rem;
  }
`;

const FollowUpButton = styled(Button)`
  margin: 0.25rem;
  padding: 0.5rem 1rem;
  background-color: #f59e0b;
  color: #000000;
  font-size: 0.9rem;
  
  &:hover {
    background-color: #d97706;
  }
`;

const LoadingSpinner = styled.div`
  text-align: center;
  padding: 2rem;
  color: #6b7280;
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

  // Check API health on component mount
  useEffect(() => {
    checkAPIHealth();
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

  const addMessage = (role, content) => {
    const newMessage = {
      role,
      content,
      time: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;
    
    const userMessage = inputValue;
    setInputValue('');
    addMessage('user', userMessage);
    setIsLoading(true);

    try {
      // Step 1: Orchestrate intent
      const orchestrationResult = await agentAPI.orchestrateIntent(
        userMessage,
        JSON.stringify(messages.slice(-5)),
        JSON.stringify(currentData || {})
      );

      if (orchestrationResult.success) {
        const actionType = orchestrationResult.data.action_type;
        addMessage('assistant', `🎯 Intent: ${actionType.toUpperCase()} (Confidence: ${Math.round(orchestrationResult.data.confidence * 100)}%)`);

        if (actionType === 'follow_up' && currentData) {
          // Handle follow-up question
          await handleFollowUpQuestion(userMessage);
        } else {
          // Handle new query
          await handleNewQuery(userMessage);
        }
      }
    } catch (error) {
      console.error('Error processing request:', error);
      addMessage('assistant', 'Sorry, I encountered an error processing your request. Please make sure the backend server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewQuery = async (userMessage) => {
    try {
      // Mock database schema (in real app, this would come from your config)
      const dbSchema = `
        Tables: vehicles, manufacturers, registrations, regions
        Key relationships: vehicles.manufacturer_id -> manufacturers.id
      `;

      // Step 1: Generate SQL
      addMessage('assistant', '🤖 Generating SQL query...');
      const sqlResult = await agentAPI.generateSQL(userMessage, dbSchema);
      
      if (!sqlResult.success) {
        throw new Error('SQL generation failed');
      }

      const initialSQL = sqlResult.data.sqlquery;
      addMessage('assistant', `📝 Generated SQL:`);
      
      // Step 2: Review SQL
      addMessage('assistant', '🔍 Reviewing SQL with GPT-4o...');
      const reviewResult = await agentAPI.reviewSQL(initialSQL, dbSchema);
      
      if (!reviewResult.success) {
        throw new Error('SQL review failed');
      }

      const reviewedSQL = reviewResult.data.reviewed_sqlquery;
      
      // Mock query execution (in real app, you'd execute against your database)
      const mockData = [
        { manufacturer: 'Toyota', count: 150 },
        { manufacturer: 'Honda', count: 120 },
        { manufacturer: 'Ford', count: 100 },
        { manufacturer: 'BMW', count: 80 }
      ];
      
      setCurrentData(mockData);
      addMessage('assistant', `✅ Retrieved ${mockData.length} rows`);

      // Step 3: Analyze data
      addMessage('assistant', '📊 Analyzing data patterns...');
      const analysisResult = await agentAPI.analyzeData(
        'manufacturer, count',
        `${mockData.length} rows × 2 columns`,
        JSON.stringify({ manufacturer: 'object', count: 'int64' }),
        JSON.stringify(mockData.slice(0, 3)),
        userMessage
      );

      if (analysisResult.success) {
        // Step 4: Create visualization
        addMessage('assistant', '🎨 Creating visualization...');
        const vizResult = await agentAPI.createVisualization(
          JSON.stringify(mockData),
          userMessage,
          analysisResult.data.recommended_visualizations.join(', '),
          analysisResult.data.analysis,
          analysisResult.data.key_findings
        );

        if (vizResult.success) {
          const plotSpec = JSON.parse(vizResult.data.plot_spec);
          setCurrentVisualization(plotSpec);
          addMessage('assistant', '✨ Visualization created successfully!');

          // Generate follow-up questions
          const followUpResult = await agentAPI.generateFollowUpQuestions(
            analysisResult.data.analysis,
            userMessage,
            analysisResult.data.key_findings.join(', '),
            dbSchema
          );

          if (followUpResult.success) {
            setFollowUpQuestions(followUpResult.data.questions);
          }
        }
      }

    } catch (error) {
      console.error('Error in new query flow:', error);
      addMessage('assistant', 'Sorry, I encountered an error processing your query.');
    }
  };

  const handleFollowUpQuestion = async (userMessage) => {
    try {
      if (userMessage.toLowerCase().includes('convert') || userMessage.toLowerCase().includes('change to')) {
        // Handle visualization conversion
        addMessage('assistant', '🎨 Creating alternative visualization...');
        const altVizResult = await agentAPI.createAlternativeVisualization(
          userMessage,
          JSON.stringify(currentData),
          currentVisualization?.type || 'bar'
        );

        if (altVizResult.success) {
          const newPlotSpec = JSON.parse(altVizResult.data.plot_spec);
          setCurrentVisualization(newPlotSpec);
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

  const handleFollowUpClick = (question) => {
    setInputValue(question);
  };

  const renderVisualization = () => {
    if (!currentVisualization) return null;

    const { type, data, layout } = currentVisualization;
    
    try {
      let plotData = [];
      
      if (type === 'bar') {
        plotData = [{
          x: data.x,
          y: data.y,
          type: 'bar',
          marker: { color: '#3b82f6' }
        }];
      } else if (type === 'pie') {
        plotData = [{
          labels: data.labels,
          values: data.values,
          type: 'pie'
        }];
      }

      return (
        <Plot
          data={plotData}
          layout={{
            ...layout,
            autosize: true,
            margin: { l: 50, r: 50, t: 50, b: 50 }
          }}
          style={{ width: '100%', height: '400px' }}
          config={{ responsive: true }}
        />
      );
    } catch (error) {
      console.error('Error rendering visualization:', error);
      return <div>Error rendering visualization</div>;
    }
  };

  return (
    <AppContainer>
      <Sidebar>
        <SidebarHeader>
          <h1>
            <FiBarChart3 />
            Visualization Agent
          </h1>
          <p>AI-powered SQL generation and visualization</p>
          <div style={{ marginTop: '0.5rem', fontSize: '0.8rem' }}>
            API Status: <span style={{ color: apiStatus === 'connected' ? '#10b981' : '#ef4444' }}>
              {apiStatus === 'connected' ? '🟢 Connected' : '🔴 Disconnected'}
            </span>
          </div>
        </SidebarHeader>
        
        <ChatContainer>
          {messages.map((message, index) => (
            <Message key={index} isUser={message.role === 'user'}>
              {message.content}
            </Message>
          ))}
          {isLoading && (
            <LoadingSpinner>
              Processing your request...
            </LoadingSpinner>
          )}
        </ChatContainer>
        
        <InputContainer>
          <InputWrapper>
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about your database..."
              disabled={isLoading}
            />
            <Button variant="primary" onClick={handleSend} disabled={isLoading}>
              <FiSend />
            </Button>
            <Button>
              <FiMic />
            </Button>
          </InputWrapper>
        </InputContainer>
      </Sidebar>

      <MainPanel>
        <h1>Ask questions about your data in natural language</h1>
        <hr />
        
        {currentVisualization ? (
          <>
            {currentData && (
              <MetricsContainer>
                <MetricCard>
                  <h3>Total Records</h3>
                  <p>{currentData.length}</p>
                </MetricCard>
                <MetricCard>
                  <h3>Unique Values</h3>
                  <p>{new Set(currentData.map(d => d.manufacturer)).size}</p>
                </MetricCard>
                <MetricCard>
                  <h3>Top Performer</h3>
                  <p>{currentData[0]?.manufacturer || 'N/A'}</p>
                </MetricCard>
              </MetricsContainer>
            )}
            
            {currentData && (
              <DataTable>
                <table>
                  <thead>
                    <tr>
                      {Object.keys(currentData[0] || {}).map(key => (
                        <th key={key}>{key}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {currentData.map((row, index) => (
                      <tr key={index}>
                        {Object.values(row).map((value, i) => (
                          <td key={i}>{value}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </DataTable>
            )}
            
            {renderVisualization()}
            
            {followUpQuestions.length > 0 && (
              <FollowUpContainer>
                <h3>💡 Suggested follow-up questions:</h3>
                {followUpQuestions.map((question, index) => (
                  <FollowUpButton
                    key={index}
                    onClick={() => handleFollowUpClick(question)}
                  >
                    {question}
                  </FollowUpButton>
                ))}
              </FollowUpContainer>
            )}
          </>
        ) : (
          <WelcomeContainer>
            <h2>📊 Ready to Visualize Your Data</h2>
            <p>
              Ask questions about your vehicle registration data in the chat, and I'll create
              beautiful visualizations for you using AI-generated SQL queries.
            </p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '2rem' }}>
              <Button onClick={() => setInputValue("Show me top brands by market share")}>
                📈 Top Brands
              </Button>
              <Button onClick={() => setInputValue("Show quarterly performance")}>
                📊 Quarterly Data
              </Button>
              <Button onClick={() => setInputValue("Compare electric vs gasoline vehicles")}>
                🔋 Fuel Types
              </Button>
            </div>
          </WelcomeContainer>
        )}
      </MainPanel>
    </AppContainer>
  );
}

export default App;
