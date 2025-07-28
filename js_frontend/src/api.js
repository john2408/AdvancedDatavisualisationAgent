// API service for communicating with FastAPI backend
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Agent API calls
export const agentAPI = {
  // SQL Generator Agent
  generateSQL: async (userInput, dbSchema) => {
    const response = await api.post('/agents/sql-generator', {
      user_input: userInput,
      db_schema: dbSchema
    });
    return response.data;
  },

  // SQL Reviewer Agent
  reviewSQL: async (sqlQuery, dbSchema) => {
    const response = await api.post('/agents/sql-reviewer', {
      sql_query: sqlQuery,
      db_schema: dbSchema
    });
    return response.data;
  },

  // Data Analysis Agent
  analyzeData: async (columns, shape, dtypes, sampleData, userQuestion) => {
    const response = await api.post('/agents/data-analysis', {
      columns,
      shape,
      dtypes,
      sample_data: sampleData,
      user_question: userQuestion
    });
    return response.data;
  },

  // Visualization Agent
  createVisualization: async (dataframeJson, userQuestion, recommendedViz, analysisSummary, keyFindings) => {
    const response = await api.post('/agents/visualization', {
      dataframe_json: dataframeJson,
      user_question: userQuestion,
      recommended_visualizations: recommendedViz,
      analysis_summary: analysisSummary,
      key_findings: keyFindings
    });
    return response.data;
  },

  // Orchestration Agent
  orchestrateIntent: async (userQuery, conversationHistory, currentDataContext) => {
    const response = await api.post('/agents/orchestration', {
      user_query: userQuery,
      conversation_history: conversationHistory,
      current_data_context: currentDataContext
    });
    return response.data;
  },

  // Data Question Agent
  answerDataQuestion: async (userQuestion, currentData, dataSummary, chartInfo) => {
    const response = await api.post('/agents/data-question', {
      user_question: userQuestion,
      current_data: currentData,
      data_summary: dataSummary,
      chart_info: chartInfo
    });
    return response.data;
  },

  // Alternative Visualization Agent
  createAlternativeVisualization: async (userRequest, currentData, currentChartType) => {
    const response = await api.post('/agents/alternative-visualization', {
      user_request: userRequest,
      current_data: currentData,
      current_chart_type: currentChartType
    });
    return response.data;
  },

  // Follow-up Questions Agent
  generateFollowUpQuestions: async (dataAnalysis, originalQuery, dataInsights, dbSchema) => {
    const response = await api.post('/agents/follow-up-questions', {
      data_analysis: dataAnalysis,
      original_query: originalQuery,
      data_insights: dataInsights,
      db_schema: dbSchema
    });
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // List all available agents
  listAgents: async () => {
    const response = await api.get('/agents/list');
    return response.data;
  }
};

export default api;
