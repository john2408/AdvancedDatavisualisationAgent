// API service for communicating with FastAPI backend
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('🚨 API Interceptor caught error:', error);
    
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('📡 API Response Error:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        headers: error.response.headers
      });
      
      // Extract error message properly
      let errorMessage = 'An error occurred';
      if (error.response.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.detail) {
          errorMessage = Array.isArray(error.response.data.detail) 
            ? error.response.data.detail.map(d => d.msg || d).join(', ')
            : error.response.data.detail;
        } else if (error.response.data.message) {
          errorMessage = error.response.data.message;
        } else if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else {
          errorMessage = JSON.stringify(error.response.data);
        }
      }
      
      throw new Error(`API Error (${error.response.status}): ${errorMessage}`);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('🌐 Network Error:', error.request);
      throw new Error('Network error - please check if the backend is running');
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('⚠️ Request Setup Error:', error.message);
      throw new Error(`Request error: ${error.message}`);
    }
  }
);

// Agent API calls
export const agentAPI = {
  // Health Check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Get list of available agents
  getAgentList: async () => {
    const response = await api.get('/agents/list');
    return response.data;
  },

  // Get Database Schema
  getDatabaseSchema: async () => {
    const response = await api.get('/config/schema');
    return response.data;
  },

  // SQL Generator Agent
  generateSQL: async (userInput, dbSchema) => {
    const response = await api.post('/agents/sql-generator', {
      user_input: userInput,
      db_schema: dbSchema
    });
    return response.data;
  },

  // Orchestration Agent
  orchestrateIntent: async (userQuery, previousContext, currentDataContext) => {
    const response = await api.post('/agents/orchestration', {
      user_input: userQuery,
      previous_context: previousContext || '',
      current_data_context: currentDataContext || '{}'
    });
    return response.data;
  },

  // SQL Review Agent - NOW REAL ENDPOINT
  reviewSQL: async (initialSQL, dbSchema) => {
    const response = await api.post('/agents/sql-reviewer', {
      sql_query: initialSQL,
      db_schema: dbSchema
    });
    return response.data;
  },

  // Execute SQL Query - NEW REAL ENDPOINT
  executeSQL: async (sqlQuery) => {
    const response = await api.post('/agents/execute-sql', {
      sql_query: sqlQuery
    });
    return response.data;
  },

  // Data Analysis Agent - NOW REAL ENDPOINT
  analyzeData: async (columns, shape, dtypes, sample_data, user_query) => {
    const response = await api.post('/agents/data-analysis', {
      columns: columns,
      shape: shape,
      dtypes: dtypes,
      sample_data: sample_data,
      user_query: user_query
    });
    return response.data;
  },

  // Visualization Creation Agent - NOW REAL ENDPOINT
  createVisualization: async (data, user_query, recommended_viz, analysis, key_findings) => {
    console.log('🐛 API createVisualization called with:', {
      data: typeof data === 'string' ? data.substring(0, 200) + '...' : data,
      user_query,
      recommended_viz,
      analysis: typeof analysis === 'string' ? analysis.substring(0, 100) + '...' : analysis,
      key_findings: typeof key_findings === 'string' ? key_findings.substring(0, 100) + '...' : key_findings
    });
    
    try {
      const response = await api.post('/agents/data-visualization', {
        data: data,
        user_query: user_query,
        recommended_viz: recommended_viz,
        analysis: analysis,
        key_findings: key_findings
      });
      
      console.log('✅ createVisualization response:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ createVisualization failed:', {
        error: error.message,
        requestData: { data, user_query, recommended_viz, analysis, key_findings }
      });
      throw error;
    }
  },

  // Follow-up Questions Generation - NOW REAL ENDPOINT
  generateFollowUpQuestions: async (analysis, original_query, key_findings, db_schema) => {
    const response = await api.post('/agents/follow-up-questions', {
      analysis: analysis,
      original_query: original_query,
      key_findings: key_findings,
      db_schema: db_schema
    });
    return response.data;
  },

  // Alternative Visualization Creation - NOW REAL ENDPOINT
  createAlternativeVisualization: async (user_request, current_data, current_chart_type) => {
    const response = await api.post('/agents/alternative-visualization', {
      user_request: user_request,
      current_data: current_data,
      current_chart_type: current_chart_type
    });
    return response.data;
  },

  // Data Question Answering - NOW REAL ENDPOINT
  answerDataQuestion: async (question, current_data, data_summary, current_visualization) => {
    const response = await api.post('/agents/data-question', {
      user_question: question,
      current_data: current_data,
      data_summary: data_summary,
      chart_info: current_visualization
    });
    return response.data;
  },

};
