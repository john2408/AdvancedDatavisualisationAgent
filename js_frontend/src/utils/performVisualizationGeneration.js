/**
 * Step 4b: Visualization Generation Module
 * Handles only the visualization creation step of the pipeline
 */

import { createDataVisualization } from './createVisualization';

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

    if (!analysisData) {
      throw new Error('Analysis data is required for visualization creation');
    }

    if (addMessage) {
      addMessage('assistant', '🎨 Creating your visualization...');
    }

    // Create visualization using existing modular function
    const vizResult = await createDataVisualization(
      data, 
      userMessage, 
      analysisData, 
      { ...callbacks, setFollowUpQuestions: (questions) => setFollowUpQuestions && setFollowUpQuestions(questions) }
    );

    if (!vizResult.success && !vizResult.fallbackCreated) {
      throw new Error(`Visualization creation failed: ${vizResult.error}`);
    }

    console.log('✅ Step 4b: Visualization generation completed successfully');
    
    if (addMessage) {
      if (vizResult.fallbackCreated) {
        addMessage('assistant', '⚠️ Created fallback visualization - some features may be limited.');
      } else {
        addMessage('assistant', '✅ Visualization created successfully!');
      }
    }

    return {
      success: true,
      data: vizResult.data,
      fallbackCreated: vizResult.fallbackCreated || false,
      message: vizResult.fallbackCreated ? 'Fallback visualization created' : 'Visualization created successfully'
    };

  } catch (error) {
    console.error('❌ Step 4b: Visualization generation failed:', error);
    
    // Try to create a basic fallback visualization
    const fallbackViz = createBasicFallbackVisualization(data, analysisData);
    
    if (fallbackViz && setCurrentVisualization) {
      console.log('⚠️ Step 4b: Created basic fallback visualization');
      setCurrentVisualization(fallbackViz);
      
      if (addMessage) {
        addMessage('assistant', '⚠️ Created basic fallback visualization due to generation error.');
      }
      
      return {
        success: false,
        error: error.message,
        fallbackCreated: true,
        data: { visualization: fallbackViz },
        step: 'visualization_generation'
      };
    }
    
    if (addMessage) {
      addMessage('assistant', `❌ VISUALIZATION ERROR: ${error.message}`);
    }
    
    return {
      success: false,
      error: error.message,
      fallbackCreated: false,
      step: 'visualization_generation'
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

    // Determine chart type from analysis or fallback to bar
    let chartType = 'bar';
    if (analysisData?.recommended_visualizations?.length > 0) {
      chartType = analysisData.recommended_visualizations[0];
    }

    // Create basic visualization spec based on chart type
    const basicVizSpec = {
      type: chartType,
      data: {
        x: data.map(d => d[categoryKey] || `Row ${data.indexOf(d) + 1}`),
        y: data.map(d => d[numericKey] || 0)
      },
      layout: {
        title: analysisData?.analysis ? 
          'Data Overview (Fallback)' : 
          'Basic Data Visualization',
        xaxis: { title: categoryKey || 'Category' },
        yaxis: { title: numericKey || 'Value' },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        font: { color: 'black' },
        showlegend: false
      },
      config: {
        responsive: true,
        displayModeBar: true,
        displaylogo: false
      }
    };

    console.log('📊 Created basic fallback visualization:', { 
      type: chartType, 
      dataPoints: data.length,
      xKey: categoryKey,
      yKey: numericKey
    });

    return basicVizSpec;

  } catch (error) {
    console.error('Failed to create basic fallback visualization:', error);
    return null;
  }
};

/**
 * Validates visualization data before processing
 * @param {Array} data - Query result data
 * @param {Object} analysisData - Analysis results
 * @returns {Object} Validation result
 */
export const validateVisualizationInput = (data, analysisData) => {
  const errors = [];
  const warnings = [];

  // Data validation
  if (!Array.isArray(data)) {
    errors.push('Data must be an array');
  } else if (data.length === 0) {
    errors.push('Data array is empty');
  } else if (data.length > 10000) {
    warnings.push(`Large dataset (${data.length} rows) may affect performance`);
  }

  // Analysis data validation
  if (!analysisData) {
    warnings.push('No analysis data provided - will use fallback analysis');
  } else {
    if (!analysisData.recommended_visualizations) {
      warnings.push('No recommended visualizations in analysis data');
    }
    if (!analysisData.analysis) {
      warnings.push('No analysis text provided');
    }
  }

  // Data structure validation
  if (data.length > 0) {
    const firstRow = data[0];
    const keys = Object.keys(firstRow);
    const numericKeys = keys.filter(key => typeof firstRow[key] === 'number');
    const stringKeys = keys.filter(key => typeof firstRow[key] === 'string');

    if (numericKeys.length === 0 && stringKeys.length === 0) {
      errors.push('No suitable data columns found for visualization');
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
};

export default performVisualizationGeneration;
