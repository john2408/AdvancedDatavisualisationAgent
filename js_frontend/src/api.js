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
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API Error:', error.response.data);
      throw new Error(error.response.data.detail || 'An error occurred');
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Network Error:', error.request);
      throw new Error('Network error - please check if the backend is running');
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Request Error:', error.message);
      throw new Error(error.message);
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

  // SQL Review Agent (Mock implementation for now - will need backend endpoint)
  reviewSQL: async (initialSQL, dbSchema) => {
    // For now, return the same SQL with a small optimization
    return {
      success: true,
      data: {
        reviewed_sqlquery: initialSQL.includes('LIMIT') ? initialSQL : initialSQL.trim() + '\nLIMIT 100;',
        review_notes: 'Added LIMIT for performance optimization',
        was_optimized: !initialSQL.includes('LIMIT')
      }
    };
  },

  // Data Analysis Agent (Mock implementation for now - will need backend endpoint)
  analyzeData: async (columns, shape, dtypes, sample_data, user_query) => {
    return {
      success: true,
      data: {
        recommended_visualizations: ['bar_chart', 'pie_chart'],
        analysis: `Data contains ${columns.split(',').length} columns with numerical and categorical data suitable for comparative analysis.`,
        key_findings: [
          'Clear ranking visible in the data',
          'Top categories dominate the distribution',
          'Good candidate for both bar and pie chart visualizations'
        ],
        chart_recommendations: {
          primary: 'bar_chart',
          alternatives: ['pie_chart', 'horizontal_bar']
        }
      }
    };
  },

  // Visualization Creation Agent (Mock implementation for now - will need backend endpoint)
  createVisualization: async (data, user_query, recommended_viz, analysis, key_findings) => {
    const parsedData = JSON.parse(data);
    const firstRow = parsedData[0] || {};
    const keys = Object.keys(firstRow);
    
    // Find categorical and numerical columns
    const categoricalKey = keys.find(key => typeof firstRow[key] === 'string');
    const numericalKey = keys.find(key => typeof firstRow[key] === 'number');
    
    const plotSpec = {
      type: 'bar',
      data: {
        x: parsedData.map(d => d[categoricalKey]),
        y: parsedData.map(d => d[numericalKey]),
        type: 'bar',
        marker: {
          color: '#3b82f6'
        }
      },
      layout: {
        title: `${categoricalKey} vs ${numericalKey}`,
        xaxis: { title: categoricalKey || 'Category' },
        yaxis: { title: numericalKey || 'Value' },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        font: { color: 'black' }
      }
    };

    return {
      success: true,
      data: {
        plot_spec: JSON.stringify(plotSpec),
        chart_type: 'bar',
        data_summary: `Generated visualization for ${parsedData.length} data points`
      }
    };
  },

  // Follow-up Questions Generation (Mock implementation for now - will need backend endpoint)
  generateFollowUpQuestions: async (analysis, original_query, key_findings, db_schema) => {
    const questions = [
      'How do these results compare across different time periods?',
      'What are the regional variations in this data?',
      'Can you break this down by additional categories?',
      'Show me the trends over time for the top performers'
    ];

    // Customize questions based on query content
    if (original_query.toLowerCase().includes('manufacturer')) {
      questions.push('Which regions contribute most to the top manufacturers?');
      questions.push('Compare electric vs conventional vehicle registrations');
    }
    if (original_query.toLowerCase().includes('electric')) {
      questions.push('How do electric vehicle registrations vary by manufacturer?');
      questions.push('What are the regional patterns for EV adoption?');
    }

    return {
      success: true,
      data: {
        questions: questions.slice(0, 4), // Return top 4 questions
        reasoning: 'Generated schema-aware follow-up questions based on current analysis'
      }
    };
  },

  // Alternative Visualization Creation (Mock implementation for now - will need backend endpoint)
  createAlternativeVisualization: async (user_request, current_data, current_chart_type) => {
    const parsedData = JSON.parse(current_data);
    const firstRow = parsedData[0] || {};
    const keys = Object.keys(firstRow);
    
    const categoricalKey = keys.find(key => typeof firstRow[key] === 'string');
    const numericalKey = keys.find(key => typeof firstRow[key] === 'number');
    
    let plotSpec;
    
    // Determine target chart type from user request
    if (user_request.toLowerCase().includes('pie')) {
      plotSpec = {
        type: 'pie',
        data: {
          labels: parsedData.map(d => d[categoricalKey]),
          values: parsedData.map(d => d[numericalKey]),
          type: 'pie',
          textinfo: 'label+percent',
          textposition: 'outside'
        },
        layout: {
          title: `${categoricalKey} Distribution (%)`,
          plot_bgcolor: 'white',
          paper_bgcolor: 'white',
          font: { color: 'black' }
        }
      };
    } else if (user_request.toLowerCase().includes('line')) {
      plotSpec = {
        type: 'line',
        data: {
          x: parsedData.map(d => d[categoricalKey]),
          y: parsedData.map(d => d[numericalKey]),
          type: 'scatter',
          mode: 'lines+markers',
          line: { color: '#3b82f6' }
        },
        layout: {
          title: `${categoricalKey} Trend`,
          xaxis: { title: categoricalKey || 'Category' },
          yaxis: { title: numericalKey || 'Value' },
          plot_bgcolor: 'white',
          paper_bgcolor: 'white',
          font: { color: 'black' }
        }
      };
    } else {
      // Default to horizontal bar if no specific type requested
      plotSpec = {
        type: 'bar',
        data: {
          x: parsedData.map(d => d[numericalKey]),
          y: parsedData.map(d => d[categoricalKey]),
          type: 'bar',
          orientation: 'h',
          marker: { color: '#10b981' }
        },
        layout: {
          title: `${categoricalKey} vs ${numericalKey} (Horizontal)`,
          xaxis: { title: numericalKey || 'Value' },
          yaxis: { title: categoricalKey || 'Category' },
          plot_bgcolor: 'white',
          paper_bgcolor: 'white',
          font: { color: 'black' }
        }
      };
    }

    return {
      success: true,
      data: {
        plot_spec: JSON.stringify(plotSpec),
        transformation_applied: 'Chart type conversion',
        chart_type: plotSpec.type
      }
    };
  },

  // Data Question Answering (Mock implementation for now - will need backend endpoint)
  answerDataQuestion: async (question, current_data, data_summary, current_visualization) => {
    const parsedData = JSON.parse(current_data);
    const dataLength = parsedData.length;
    
    // Generate basic insights based on the data
    let answer = `Based on the current data with ${dataLength} records: `;
    
    if (question.toLowerCase().includes('top') || question.toLowerCase().includes('highest')) {
      const firstRow = parsedData[0] || {};
      const categoricalKey = Object.keys(firstRow).find(key => typeof firstRow[key] === 'string');
      if (categoricalKey && firstRow[categoricalKey]) {
        answer += `The top performer appears to be ${firstRow[categoricalKey]}.`;
      }
    } else if (question.toLowerCase().includes('total') || question.toLowerCase().includes('sum')) {
      const firstRow = parsedData[0] || {};
      const numericalKey = Object.keys(firstRow).find(key => typeof firstRow[key] === 'number');
      if (numericalKey) {
        const total = parsedData.reduce((sum, row) => sum + (row[numericalKey] || 0), 0);
        answer += `The total ${numericalKey} across all categories is ${total.toLocaleString()}.`;
      }
    } else {
      answer += `The data shows ${dataLength} categories with varying performance levels. The visualization provides a clear overview of the distribution.`;
    }

    return {
      success: true,
      data: {
        answer: answer,
        confidence: 0.85,
        data_points_analyzed: dataLength
      }
    };
  },

};
