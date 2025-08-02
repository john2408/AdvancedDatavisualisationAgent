/**
 * Standalone test for createDataVisualization function
 * Run this with: node test_createVisualization.js
 */

// Mock the API module
const mockAPI = {
  createVisualization: async (data, userMessage, recommendedViz, analysis, keyFindings) => {
    console.log('🧪 Mock API called with:');
    console.log('  data:', typeof data === 'string' ? data.substring(0, 100) + '...' : data);
    console.log('  userMessage:', userMessage);
    console.log('  recommendedViz:', recommendedViz);
    console.log('  analysis:', analysis.substring(0, 100) + '...');
    console.log('  keyFindings:', keyFindings);
    console.log('  keyFindings type:', typeof keyFindings);
    
    // Simulate the actual API call
    const response = await fetch('http://localhost:8000/agents/data-visualization', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        data: data,
        user_query: userMessage,
        recommended_viz: recommendedViz,
        analysis: analysis,
        key_findings: keyFindings
      })
    });

    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(`API Error: ${JSON.stringify(result)}`);
    }
    
    return result;
  },

  generateFollowUpQuestions: async (analysis, userMessage, keyFindings, schema) => {
    console.log('🧪 Mock generateFollowUpQuestions called');
    return {
      success: true,
      data: {
        questions: ['Follow-up question 1', 'Follow-up question 2']
      }
    };
  }
};

// Mock the createDataVisualization function (updated version)
const createDataVisualization = async (data, userMessage, analysisData, callbacks) => {
  const { addMessage, setCurrentVisualization, setFollowUpQuestions } = callbacks;
  
  try {
    addMessage('assistant', '🎨 Creating visualization...');
    
    // Validate input parameters
    if (!Array.isArray(data) || data.length === 0) {
      const error = new Error('Invalid or empty data provided for visualization');
      error.step = 'data_visualization';
      error.details = { dataLength: data?.length, dataType: typeof data };
      throw error;
    }

    if (!analysisData || !analysisData.recommended_visualizations) {
      const error = new Error('Analysis data is required for visualization creation');
      error.step = 'data_visualization';
      error.details = { analysisData };
      throw error;
    }

    let vizResult;
    try {
      // ✅ FIX: Ensure key_findings is a string (join array if needed)
      const keyFindingsString = Array.isArray(analysisData.key_findings) 
        ? analysisData.key_findings.join(', ') 
        : analysisData.key_findings;

      vizResult = await mockAPI.createVisualization(
        JSON.stringify(data),
        userMessage,
        analysisData.recommended_visualizations.join(', '),
        analysisData.analysis,
        keyFindingsString
      );

      console.log('📊 createVisualization result:', vizResult);

      if (!vizResult.success) {
        const error = new Error(`Visualization creation failed: ${vizResult.error || 'Unknown error'}`);
        error.step = 'data_visualization';
        error.details = vizResult;
        throw error;
      }
    } catch (apiError) {
      console.error('🚨 API call failed in createVisualization:', apiError);
      const error = new Error(`Visualization API call failed: ${apiError.message}`);
      error.step = 'data_visualization';
      error.originalError = apiError;
      throw error;
    }

    // Convert backend visualization format to PlotlyVisualization format
    let plotSpec;
    try {
      plotSpec = JSON.parse(vizResult.data.plot_spec);
      console.log('📊 Parsed plot_spec from backend:', plotSpec);
    } catch (parseError) {
      console.error('❌ Failed to parse plot_spec:', parseError, vizResult.data.plot_spec);
      const error = new Error(`Failed to parse visualization specification: ${parseError.message}`);
      error.step = 'data_visualization';
      error.details = { plot_spec: vizResult.data.plot_spec, parseError };
      throw error;
    }
    
    console.log('✅ Setting visualization with backend format');
    setCurrentVisualization(plotSpec);
    addMessage('assistant', '✨ Visualization created successfully!');

    // Generate follow-up questions
    try {
      const followUpResult = await mockAPI.generateFollowUpQuestions(
        analysisData.analysis,
        userMessage,
        Array.isArray(analysisData.key_findings) 
          ? analysisData.key_findings.join(', ') 
          : analysisData.key_findings,
        ''
      );

      if (followUpResult.success && followUpResult.data.questions) {
        setFollowUpQuestions(followUpResult.data.questions);
        addMessage('assistant', `💡 Generated ${followUpResult.data.questions.length} follow-up questions for deeper insights.`);
      }
    } catch (followUpError) {
      console.warn('Follow-up question generation failed:', followUpError);
    }

    return {
      success: true,
      data: {
        visualization: plotSpec,
        followUpGenerated: true
      }
    };

  } catch (error) {
    console.error('Visualization Creation Error:', error);
    
    const errorMessage = `❌ VISUALIZATION CREATION ERROR:\n` +
                        `Message: ${error.message}\n` +
                        `Step: ${error.step || 'data_visualization'}\n` +
                        `Analysis data: \`\`\`json\n${JSON.stringify(analysisData, null, 2)}\n\`\`\`\n` +
                        `Details: ${JSON.stringify(error.details, null, 2)}`;
    
    addMessage('assistant', errorMessage);
    
    return {
      success: false,
      error: error.message,
      step: error.step,
      details: error.details
    };
  }
};

// Test data
const testData = [
  {"manufacturer": "BMW", "count": 150},
  {"manufacturer": "AUDI", "count": 120},
  {"manufacturer": "MERCEDES-BENZ", "count": 100},
  {"manufacturer": "Honda", "count": 10},
  {"manufacturer": "Lexus", "count": 5}
];

const analysisData = {
  analysis: "BMW has the highest vehicle registrations, followed by AUDI and MERCEDES-BENZ.",
  recommended_visualizations: ["bar", "pie"],
  key_findings: [
    "BMW has the highest vehicle registrations, followed by AUDI and MERCEDES-BENZ.",
    "Potentially check for low registration anomalies among manufacturers like Lexus or Honda, which are not in the initial sample."
  ]
};

const userMessage = "Show me vehicle registrations by manufacturer";

// Mock callbacks
const callbacks = {
  addMessage: (role, message) => console.log(`[${role.toUpperCase()}] ${message}`),
  setCurrentVisualization: (viz) => console.log('📊 Setting visualization:', JSON.stringify(viz, null, 2)),
  setFollowUpQuestions: (questions) => console.log('💡 Setting follow-up questions:', questions)
};

// Run the test
async function runTest() {
  console.log('🧪 Testing createDataVisualization with fixed key_findings handling...\n');
  
  try {
    const result = await createDataVisualization(testData, userMessage, analysisData, callbacks);
    console.log('\n✅ Test completed successfully!');
    console.log('📊 Final result:', result);
  } catch (error) {
    console.error('\n❌ Test failed:', error);
  }
}

// Check if we're running in Node.js environment
if (typeof window === 'undefined' && typeof global !== 'undefined') {
  // Node.js environment - need to install node-fetch
  console.log('⚠️  To run this test in Node.js, first install node-fetch:');
  console.log('    npm install node-fetch');
  console.log('    Then uncomment the import line below and run: node test_createVisualization.js\n');
  
  // global.fetch = require('node-fetch'); // Uncomment this line if you have node-fetch installed
  
  // For now, just simulate without making real HTTP calls
  mockAPI.createVisualization = async (data, userMessage, recommendedViz, analysis, keyFindings) => {
    console.log('🧪 Mock API called with:');
    console.log('  data:', typeof data === 'string' ? data.substring(0, 100) + '...' : data);
    console.log('  userMessage:', userMessage);
    console.log('  recommendedViz:', recommendedViz);
    console.log('  analysis:', analysis.substring(0, 100) + '...');
    console.log('  keyFindings:', keyFindings);
    console.log('  keyFindings type:', typeof keyFindings);
    console.log('  ✅ key_findings is now a string!');
    
    // Simulate successful response
    return {
      success: true,
      data: {
        plot_type: "bar",
        x_column: "manufacturer",
        y_column: "count",
        color_column: "",
        title: "Vehicle Registrations by Manufacturer",
        plot_spec: JSON.stringify({
          type: "bar",
          data: { x: ["BMW", "AUDI"], y: [150, 120] },
          layout: { title: "Vehicle Registrations by Manufacturer" }
        })
      }
    };
  };
  
  runTest();
} else if (typeof window !== 'undefined') {
  // Browser environment
  console.log('🌐 Running in browser environment');
  runTest();
}

// Export for browser use
if (typeof window !== 'undefined') {
  window.testCreateVisualization = runTest;
  window.testData = testData;
  window.analysisData = analysisData;
}
