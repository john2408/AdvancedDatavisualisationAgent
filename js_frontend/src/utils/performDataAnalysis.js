/**
 * Step 4a: Data Analysis Module
 * Handles only the data analysis step of the pipeline
 */

import { analyzeQueryData } from './dataAnalysis';

/**
 * Performs data analysis on query results
 * @param {Array} data - Query result data
 * @param {string} userMessage - User's original question
 * @param {Object} callbacks - Callback functions for UI updates
 * @returns {Promise<Object>} Analysis result with success flag
 */
export const performDataAnalysis = async (data, userMessage, callbacks = {}) => {
  const { addMessage } = callbacks;
  
  console.log('📊 Step 4a: Starting data analysis...');
  
  try {
    // Validate input data
    if (!Array.isArray(data) || data.length === 0) {
      throw new Error('No data provided for analysis');
    }

    if (addMessage) {
      addMessage('assistant', '🔍 Analyzing your data...');
    }

    // Perform data analysis using existing modular function
    const analysisResult = await analyzeQueryData(data, userMessage, callbacks);
    
    if (!analysisResult.success) {
      throw new Error(`Data analysis failed: ${analysisResult.error}`);
    }

    console.log('✅ Step 4a: Data analysis completed successfully');
    
    if (addMessage) {
      addMessage('assistant', '✅ Data analysis complete! Key insights identified.');
    }

    return {
      success: true,
      data: analysisResult.data,
      message: 'Data analysis completed successfully'
    };

  } catch (error) {
    console.error('❌ Step 4a: Data analysis failed:', error);
    
    if (addMessage) {
      addMessage('assistant', `❌ DATA ANALYSIS ERROR: ${error.message}`);
    }
    
    return {
      success: false,
      error: error.message,
      step: 'data_analysis'
    };
  }
};

/**
 * Creates a minimal analysis result for fallback scenarios
 * @param {Array} data - Query result data
 * @param {string} userMessage - User's original question
 * @returns {Object} Basic analysis result
 */
export const createFallbackAnalysis = (data, userMessage) => {
  try {
    if (!Array.isArray(data) || data.length === 0) {
      return {
        analysis: 'No data available for analysis',
        recommended_visualizations: ['bar'],
        key_findings: 'No data to analyze'
      };
    }

    const keys = Object.keys(data[0] || {});
    const numericKeys = keys.filter(key => typeof data[0][key] === 'number');
    const categoryKeys = keys.filter(key => typeof data[0][key] === 'string');
    
    // Basic analysis
    const totalRecords = data.length;
    const hasNumericData = numericKeys.length > 0;
    const hasCategoricalData = categoryKeys.length > 0;
    
    let analysis = `Analysis of ${totalRecords} records found `;
    if (hasNumericData && hasCategoricalData) {
      analysis += `numeric data (${numericKeys.join(', ')}) and categorical data (${categoryKeys.join(', ')}).`;
    } else if (hasNumericData) {
      analysis += `numeric data in columns: ${numericKeys.join(', ')}.`;
    } else if (hasCategoricalData) {
      analysis += `categorical data in columns: ${categoryKeys.join(', ')}.`;
    } else {
      analysis += 'mixed data types.';
    }

    // Recommend visualization based on data structure
    let recommendedViz = ['bar'];
    if (hasNumericData && hasCategoricalData) {
      recommendedViz = ['bar', 'pie', 'line'];
    } else if (numericKeys.length > 1) {
      recommendedViz = ['scatter', 'line', 'bar'];
    }

    // Basic key findings
    let keyFindings = `Dataset contains ${totalRecords} records`;
    if (hasNumericData) {
      const firstNumericCol = numericKeys[0];
      const values = data.map(d => d[firstNumericCol]).filter(v => typeof v === 'number');
      if (values.length > 0) {
        const max = Math.max(...values);
        const min = Math.min(...values);
        keyFindings += `, with ${firstNumericCol} ranging from ${min} to ${max}`;
      }
    }
    keyFindings += '.';

    return {
      analysis,
      recommended_visualizations: recommendedViz,
      key_findings: keyFindings
    };

  } catch (error) {
    console.error('Failed to create fallback analysis:', error);
    return {
      analysis: 'Unable to analyze data',
      recommended_visualizations: ['bar'],
      key_findings: 'Analysis failed'
    };
  }
};

export default performDataAnalysis;
