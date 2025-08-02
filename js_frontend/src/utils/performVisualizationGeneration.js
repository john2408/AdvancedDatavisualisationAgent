/**
 * Step 4b: Visualization Generation Module
 * Handles only the visualization creation step of the pipeline
 */

import { agentAPI } from '../api';

/**
 * Performs visualization generation based on data and analysis results
 * @param {Array} data - Query result data
 * @param {string} userMessage - User's original question
 * @param {Object} analysisData - Results from data analysis step
 * @param {Object} callbacks - Callback functions for UI updates
 * @returns {Promise<Object>} Visualization result with success flag
 */
export const performVisualizationGeneration = async (data, userMessage, analysisData, callbacks = {}) => {
  const { addMessage, setCurrentVisualization, setFollowUpQuestions } = callbacks;
  
  console.log('🎨 Step 4b: Starting visualization generation...');
  
  try {
    // Validate input data
    if (!Array.isArray(data) || data.length === 0) {
      throw new Error('No data provided for visualization');
    }

    if (!analysisData || !analysisData.recommended_visualizations) {
      throw new Error('Analysis data with recommended visualizations is required');
    }

    if (addMessage) {
      addMessage('assistant', '🎨 Creating your visualization...');
    }

    // Call the API to create visualization
    const keyFindingsString = Array.isArray(analysisData.key_findings) 
      ? analysisData.key_findings.join(', ') 
      : analysisData.key_findings || '';

    console.log('📊 Calling createVisualization API...');
    const vizResult = await agentAPI.createVisualization(
      JSON.stringify(data),
      userMessage,
      analysisData.recommended_visualizations.join(', '),
      analysisData.analysis,
      keyFindingsString
    );

    if (!vizResult.success) {
      throw new Error(`API call failed: ${vizResult.error || 'Unknown error'}`);
    }

    // Parse the plot_spec from backend
    let plotSpec;
    try {
      plotSpec = JSON.parse(vizResult.data.plot_spec);
      console.log('📊 Parsed plot_spec from backend:', plotSpec);
      console.log('🐛 plotSpec.data.x:', plotSpec.data?.x);
      console.log('🐛 plotSpec.data.y:', plotSpec.data?.y);
    } catch (parseError) {
      throw new Error(`Failed to parse visualization specification: ${parseError.message}`);
    }
    
    // Set the visualization (PlotlyVisualization component handles backend format)
    console.log('✅ Setting visualization with backend format');
    setCurrentVisualization(plotSpec);
    
    if (addMessage) {
      addMessage('assistant', '✨ Visualization created successfully!');
    }

    // Generate follow-up questions if callback is available
    if (setFollowUpQuestions) {
      try {
        const followUpResult = await agentAPI.generateFollowUpQuestions(
          analysisData.analysis,
          userMessage,
          keyFindingsString,
          ''
        );
        if (followUpResult.success && followUpResult.data.questions) {
          setFollowUpQuestions(followUpResult.data.questions);
        }
      } catch (followUpError) {
        console.warn('Follow-up question generation failed:', followUpError);
      }
    }

    console.log('✅ Step 4b: Visualization generation completed successfully');
    
    return {
      success: true,
      data: { visualization: plotSpec },
      message: 'Visualization created successfully'
    };

  } catch (error) {
    console.error('❌ Step 4b: Visualization generation failed:', error);
    
    // Try to create a basic fallback visualization
    const fallbackViz = createBasicFallbackVisualization(data, analysisData);
    
    if (fallbackViz && setCurrentVisualization) {
      console.log('⚠️ Step 4b: Created basic fallback visualization');
      setCurrentVisualization(fallbackViz);
      
      if (addMessage) {
        addMessage('assistant', '⚠️ Created basic fallback visualization due to API error.');
      }
      
      return {
        success: true,
        data: { visualization: fallbackViz },
        fallbackCreated: true,
        message: 'Fallback visualization created'
      };
    }
    
    if (addMessage) {
      addMessage('assistant', `❌ VISUALIZATION ERROR: ${error.message}`);
    }
    
    return {
      success: false,
      error: error.message,
      message: 'Visualization creation failed'
    };
  }
};

/**
 * Creates a basic fallback visualization when the main generation fails
 * @param {Array} data - Query result data
 * @param {Object} analysisData - Analysis results (optional)
 * @returns {Object|null} Basic visualization specification or null
 */
export const createBasicFallbackVisualization = (data, analysisData = null) => {
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

    // Create simple bar chart (backend format for consistency)
    return {
      type: 'bar',
      data: {
        x: data.map(d => d[categoryKey] || `Row ${data.indexOf(d) + 1}`),
        y: data.map(d => d[numericKey] || 0)
      },
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
    console.error('Failed to create basic fallback visualization:', error);
    return null;
  }
};

/**
 * Create alternative visualization for follow-up questions
 * @param {string} userMessage - User's request for alternative visualization
 * @param {Array} currentData - Current data set
 * @param {string} currentVizType - Current visualization type
 * @param {Object} callbacks - Callback functions
 * @returns {Promise<Object>} Alternative visualization result
 */
export const createAlternativeVisualization = async (userMessage, currentData, currentVizType, callbacks) => {
  const { addMessage, setCurrentVisualization } = callbacks;
  
  try {
    if (addMessage) {
      addMessage('assistant', '🎨 Creating alternative visualization...');
    }
    
    // Call API for alternative visualization
    const altVizResult = await agentAPI.createAlternativeVisualization(
      userMessage,
      JSON.stringify(currentData),
      currentVizType
    );

    if (!altVizResult.success) {
      throw new Error(`Alternative visualization failed: ${altVizResult.error || 'Unknown error'}`);
    }

    // Parse the plot_spec from backend
    let plotSpec;
    try {
      plotSpec = JSON.parse(altVizResult.data.plot_spec);
    } catch (parseError) {
      throw new Error(`Failed to parse alternative visualization: ${parseError.message}`);
    }
    
    // Set the alternative visualization
    setCurrentVisualization(plotSpec);
    
    if (addMessage) {
      addMessage('assistant', '✨ Alternative visualization created!');
    }

    return {
      success: true,
      data: { visualization: plotSpec }
    };

  } catch (error) {
    console.error('Alternative Visualization Error:', error);
    
    if (addMessage) {
      addMessage('assistant', `❌ ALTERNATIVE VISUALIZATION ERROR: ${error.message}`);
    }
    
    return {
      success: false,
      error: error.message
    };
  }
};


export default performVisualizationGeneration;
