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
  // Health Check
  healthCheck: async () => {
    const response = await api.get('/health');
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
  orchestrateIntent: async (userQuery, conversationHistory, currentDataContext) => {
    const response = await api.post('/agents/orchestration', {
      user_query: userQuery,
      conversation_history: conversationHistory,
      current_data_context: currentDataContext
    });
    return response.data;
  },

  // Mock implementations for missing endpoints
  reviewSQL: async (sqlQuery, dbSchema) => {
    // Mock implementation until backend endpoint is available
    return {
      success: true,
      data: {
        reviewed_sqlquery: sqlQuery,
        agent_type: "sql_reviewer",
        mode: "mock"
      }
    };
  },

  analyzeData: async (columns, shape, dtypes, sampleData, userQuestion) => {
    // Mock implementation
    return {
      success: true,
      data: {
        analysis: "Mock data analysis: The data shows interesting patterns.",
        recommended_visualizations: ["bar", "pie"],
        key_findings: ["Top manufacturer is Toyota", "Electric vehicles are growing"],
        agent_type: "data_analyzer",
        mode: "mock"
      }
    };
  },

  createVisualization: async (dataframeJson, userQuestion, recommendedViz, analysis, keyFindings) => {
    // Mock implementation
    const mockPlotSpec = {
      type: "bar",
      data: {
        x: ["Toyota", "Honda", "Ford", "BMW"],
        y: [150, 120, 100, 80]
      },
      layout: {
        title: "Vehicle Count by Manufacturer",
        xaxis: { title: "Manufacturer" },
        yaxis: { title: "Count" }
      }
    };

    return {
      success: true,
      data: {
        plot_spec: JSON.stringify(mockPlotSpec),
        plot_type: "bar",
        title: "Vehicle Count by Manufacturer",
        agent_type: "visualization_creator",
        mode: "mock"
      }
    };
  },

  generateFollowUpQuestions: async (dataAnalysis, originalQuery, dataInsights, dbSchema) => {
    // Mock implementation
    return {
      success: true,
      data: {
        questions: [
          "Which manufacturer has the highest growth rate?",
          "Show me the trend over the last 12 months",
          "How do electric vehicle registrations compare to gasoline?",
          "What are the seasonal patterns in registrations?"
        ],
        categories: ["trends", "comparisons", "insights"],
        agent_type: "follow_up_generator",
        mode: "mock"
      }
    };
  },

  createAlternativeVisualization: async (userRequest, currentData, currentChartType) => {
    // Mock implementation for alternative visualization
    const mockPlotSpec = {
      type: "pie",
      data: {
        labels: ["Toyota", "Honda", "Ford", "BMW"],
        values: [150, 120, 100, 80]
      },
      layout: {
        title: "Market Share by Manufacturer"
      }
    };

    return {
      success: true,
      data: {
        plot_spec: JSON.stringify(mockPlotSpec),
        plot_type: "pie",
        title: "Market Share by Manufacturer",
        agent_type: "alternative_visualization",
        mode: "mock"
      }
    };
  },

  answerDataQuestion: async (userQuestion, currentData, dataSummary, chartInfo) => {
    // Mock implementation for data questions
    return {
      success: true,
      data: {
        answer: "Based on your current data, Toyota leads with 150 registrations, followed by Honda with 120. This represents a significant market dominance by Japanese manufacturers.",
        referenced_data_points: ["Toyota: 150", "Honda: 120"],
        insights: ["Japanese manufacturers dominate", "Top 2 brands account for 60% of market"],
        agent_type: "data_question_answerer",
        mode: "mock"
      }
    };
  }
};
