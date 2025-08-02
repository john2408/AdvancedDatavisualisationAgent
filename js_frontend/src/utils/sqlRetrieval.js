import { agentAPI } from '../api';

/**
 * SQL Retrieval Module - Handles Step 1 (SQL Generation) and Step 2 (SQL Review)
 */

export const generateAndReviewSQL = async (userMessage, dbSchema, callbacks) => {
  const { updatePipelineStep, completePipelineStep, addMessage } = callbacks;
  
  try {
    // Step 1: Generate SQL
    updatePipelineStep('sql_generation');
    addMessage('assistant', '🤖 Generating SQL query...');
    
    const sqlResult = await agentAPI.generateSQL(userMessage, dbSchema);
    
    if (!sqlResult.success) {
      const error = new Error(`SQL generation failed: ${sqlResult.error || 'Unknown error'}`);
      error.step = 'sql_generation';
      error.details = sqlResult;
      throw error;
    }

    const initialSQL = sqlResult.data.sqlquery;
    completePipelineStep('sql_generation');
    addMessage('assistant', `📝 Generated SQL Query:\n\`\`\`sql\n${initialSQL}\n\`\`\``);
    
    // Step 2: Review SQL
    updatePipelineStep('sql_review');
    addMessage('assistant', '🔍 Reviewing SQL with GPT-4o verifier...');
    
    const reviewResult = await agentAPI.reviewSQL(initialSQL, dbSchema);
    
    if (!reviewResult.success) {
      const error = new Error(`SQL review failed: ${reviewResult.error || 'Unknown error'}`);
      error.step = 'sql_review';
      error.details = reviewResult;
      error.initialSQL = initialSQL;
      throw error;
    }

    const reviewedSQL = reviewResult.data.reviewed_sqlquery;
    const wasChanged = initialSQL.trim() !== reviewedSQL.trim();
    
    completePipelineStep('sql_review');
    
    if (wasChanged) {
      addMessage('assistant', `✅ SQL optimized and improved:\n\`\`\`sql\n${reviewedSQL}\n\`\`\``);
    } else {
      addMessage('assistant', '✅ SQL validated - no changes needed');
    }

    return {
      success: true,
      data: {
        initialSQL,
        reviewedSQL,
        wasChanged
      }
    };

  } catch (error) {
    console.error('SQL Retrieval Error:', error);
    
    // Enhanced error reporting for frontend
    const errorMessage = `❌ ${error.step?.toUpperCase() || 'SQL RETRIEVAL'} ERROR:\n` +
                        `Message: ${error.message}\n` +
                        `Step: ${error.step || 'unknown'}\n` +
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
