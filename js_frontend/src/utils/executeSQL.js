import { agentAPI } from '../api';

/**
 * SQL Execution Module - Handles Step 3 (Query Execution)
 */

export const executeSQLQuery = async (sqlQuery, callbacks) => {
  const { updatePipelineStep, completePipelineStep, addMessage, setCurrentData } = callbacks;
  
  try {
    // Step 3: Execute Query
    updatePipelineStep('query_execution');
    addMessage('assistant', '🔄 Executing SQL query...');
    
    const executionResult = await agentAPI.executeSQL(sqlQuery);
    
    if (!executionResult.success) {
      const error = new Error(`SQL execution failed: ${executionResult.error || 'Unknown error'}`);
      error.step = 'query_execution';
      error.details = executionResult;
      error.sqlQuery = sqlQuery;
      throw error;
    }

    const queryData = executionResult.data.results;
    const metadata = executionResult.data.metadata;
    
    // Validate data format
    if (!Array.isArray(queryData) || queryData.length === 0) {
      const error = new Error('SQL execution returned empty or invalid data');
      error.step = 'query_execution';
      error.details = { queryData, metadata };
      error.sqlQuery = sqlQuery;
      throw error;
    }
    
    setCurrentData(queryData);
    completePipelineStep('query_execution');
    addMessage('assistant', `✅ Retrieved ${metadata.row_count} rows successfully\n` +
                           `📊 Sample data:\n\`\`\`json\n${JSON.stringify(queryData.slice(0, 3), null, 2)}\n\`\`\``);

    return {
      success: true,
      data: {
        queryData,
        metadata
      }
    };

  } catch (error) {
    console.error('SQL Execution Error:', error);
    
    // Enhanced error reporting for frontend
    const errorMessage = `❌ QUERY EXECUTION ERROR:\n` +
                        `Message: ${error.message}\n` +
                        `SQL Query: \`\`\`sql\n${error.sqlQuery || 'N/A'}\n\`\`\`\n` +
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
