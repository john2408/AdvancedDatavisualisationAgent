import { agentAPI } from '../api';

/**
 * Visualization Creation Module - Handles Step 4b (Visualization Creation)
 */

export const createDataVisualization = async (data, userMessage, analysisData, callbacks) => {
  const { addMessage, setCurrentVisualization, setFollowUpQuestions } = callbacks;
  
  try {
    // Step 4b: Create visualization
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

    const vizResult = await agentAPI.createVisualization(
      JSON.stringify(data),
      userMessage,
      analysisData.recommended_visualizations.join(', '),
      analysisData.analysis,
      analysisData.key_findings
    );

    if (!vizResult.success) {
      const error = new Error(`Visualization creation failed: ${vizResult.error || 'Unknown error'}`);
      error.step = 'data_visualization';
      error.details = vizResult;
      throw error;
    }

    // Convert backend visualization format to Plotly format
    let plotSpec;
    try {
      plotSpec = JSON.parse(vizResult.data.plot_spec);
    } catch (parseError) {
      const error = new Error(`Failed to parse visualization specification: ${parseError.message}`);
      error.step = 'data_visualization';
      error.details = { plot_spec: vizResult.data.plot_spec, parseError };
      throw error;
    }
    
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
    try {
      const followUpResult = await agentAPI.generateFollowUpQuestions(
        analysisData.analysis,
        userMessage,
        analysisData.key_findings.join(', '),
        '' // dbSchema - will be passed from caller
      );

      if (followUpResult.success && followUpResult.data.questions) {
        setFollowUpQuestions(followUpResult.data.questions);
        addMessage('assistant', `💡 Generated ${followUpResult.data.questions.length} follow-up questions for deeper insights.`);
      }
    } catch (followUpError) {
      console.warn('Follow-up question generation failed:', followUpError);
      // Don't fail the entire visualization process for follow-up questions
    }

    return {
      success: true,
      data: {
        visualization: processedViz,
        followUpGenerated: true
      }
    };

  } catch (error) {
    console.error('Visualization Creation Error:', error);
    
    // Create fallback visualization
    const fallbackViz = createFallbackVisualization(data);
    if (fallbackViz) {
      setCurrentVisualization(fallbackViz);
      addMessage('assistant', '⚠️ Created basic fallback visualization due to error in main visualization creation.');
    }
    
    // Enhanced error reporting for frontend
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
      details: error.details,
      fallbackCreated: !!fallbackViz
    };
  }
};

/**
 * Create a simple fallback visualization when main visualization fails
 */
const createFallbackVisualization = (data) => {
  try {
    if (!Array.isArray(data) || data.length === 0) {
      return null;
    }

    const keys = Object.keys(data[0] || {});
    const numericKey = keys.find(key => typeof data[0][key] === 'number');
    const categoryKey = keys.find(key => typeof data[0][key] === 'string');
    
    if (!numericKey && !categoryKey) {
      return null;
    }
    
    return {
      type: 'bar',
      data: [{
        x: data.map(d => d[categoryKey] || `Row ${data.indexOf(d) + 1}`),
        y: data.map(d => d[numericKey] || 0),
        type: 'bar'
      }],
      layout: {
        title: 'Data Overview (Fallback)',
        xaxis: { title: categoryKey || 'Category' },
        yaxis: { title: numericKey || 'Value' },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        font: { color: 'black' }
      }
    };
  } catch (error) {
    console.error('Failed to create fallback visualization:', error);
    return null;
  }
};

/**
 * Create alternative visualization for follow-up questions
 */
export const createAlternativeVisualization = async (userMessage, currentData, currentVizType, callbacks) => {
  const { addMessage, setCurrentVisualization } = callbacks;
  
  try {
    addMessage('assistant', '🎨 Creating alternative visualization...');
    
    const altVizResult = await agentAPI.createAlternativeVisualization(
      userMessage,
      JSON.stringify(currentData),
      currentVizType
    );

    if (!altVizResult.success) {
      const error = new Error(`Alternative visualization failed: ${altVizResult.error || 'Unknown error'}`);
      error.step = 'alternative_visualization';
      error.details = altVizResult;
      throw error;
    }

    // Convert backend visualization format to Plotly format
    let plotSpec;
    try {
      plotSpec = JSON.parse(altVizResult.data.plot_spec);
    } catch (parseError) {
      const error = new Error(`Failed to parse alternative visualization: ${parseError.message}`);
      error.step = 'alternative_visualization';
      error.details = { plot_spec: altVizResult.data.plot_spec, parseError };
      throw error;
    }
    
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

    return {
      success: true,
      data: {
        visualization: processedViz
      }
    };

  } catch (error) {
    console.error('Alternative Visualization Error:', error);
    
    // Enhanced error reporting for frontend
    const errorMessage = `❌ ALTERNATIVE VISUALIZATION ERROR:\n` +
                        `Message: ${error.message}\n` +
                        `Step: ${error.step || 'alternative_visualization'}\n` +
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
