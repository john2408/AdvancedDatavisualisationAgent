import { agentAPI } from '../api';

/**
 * Data Analysis Module - Handles Step 4a (Data Analysis)
 */

export const analyzeQueryData = async (data, userMessage, callbacks) => {
  const { addMessage } = callbacks;
  
  try {
    // Step 4a: Analyze data
    addMessage('assistant', '📊 Analyzing data patterns...');
    
    // Validate input data
    if (!Array.isArray(data) || data.length === 0) {
      const error = new Error('Invalid or empty data provided for analysis');
      error.step = 'data_analysis';
      error.details = { dataLength: data?.length, dataType: typeof data };
      throw error;
    }

    const analysisResult = await agentAPI.analyzeData(
      Object.keys(data[0] || {}).join(', '),
      `${data.length} rows × ${Object.keys(data[0] || {}).length} columns`,
      JSON.stringify(Object.keys(data[0] || {}).reduce((acc, key) => ({ ...acc, [key]: 'string' }), {})),
      JSON.stringify(data.slice(0, 3)),
      userMessage
    );

    if (!analysisResult.success) {
      const error = new Error(`Data analysis failed: ${analysisResult.error || 'Unknown error'}`);
      error.step = 'data_analysis';
      error.details = analysisResult;
      throw error;
    }

    const analysisData = analysisResult.data;
    
    // Validate analysis result structure
    if (!analysisData.recommended_visualizations || !analysisData.analysis || !analysisData.key_findings) {
      const error = new Error('Analysis returned incomplete data structure');
      error.step = 'data_analysis';
      error.details = analysisData;
      throw error;
    }

    addMessage('assistant', `📈 Analysis complete!\n` +
                           `Recommended visualization: ${analysisData.recommended_visualizations[0]}\n` +
                           `Key findings: ${analysisData.key_findings.join(', ')}`);

    return {
      success: true,
      data: analysisData
    };

  } catch (error) {
    console.error('Data Analysis Error:', error);
    
    // Enhanced error reporting for frontend
    const errorMessage = `❌ DATA ANALYSIS ERROR:\n` +
                        `Message: ${error.message}\n` +
                        `Step: ${error.step || 'data_analysis'}\n` +
                        `Data sample: \`\`\`json\n${JSON.stringify(data?.slice(0, 2), null, 2)}\n\`\`\`\n` +
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
