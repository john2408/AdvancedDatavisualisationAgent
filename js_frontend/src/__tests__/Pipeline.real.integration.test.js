/**
 * Real Integration Test for Complete Pipeline with Live Backend
 * Tests the actual API endpoints with the question: "Which car manufacturers registered the most vehicles?"
 * Validates each pipeline step as per README architecture
 */

import { agentAPI } from '../api';

// Test configuration
const TEST_QUERY = "Which car manufacturers registered the most vehicles?";
const API_TIMEOUT = 30000; // 30 seconds for real API calls

describe('Real Pipeline Integration Test - Car Manufacturers Query', () => {
  
  // Shared variables across tests
  let generatedSQL;
  let reviewedSQL;
  let queryResults;
  let queryMetadata;
  let analysisResults;
  
  beforeAll(() => {
    // Increase timeout for real API calls
    jest.setTimeout(API_TIMEOUT);
  });

  test('Step 0: Health Check - API is accessible', async () => {
    const healthResponse = await agentAPI.healthCheck();
    
    expect(healthResponse).toHaveProperty('status', 'healthy');
    expect(healthResponse).toHaveProperty('message');
    console.log('✅ Health Check:', healthResponse);
  });

  test('Step 0: Database Schema - Schema is loaded correctly', async () => {
    const schemaResponse = await agentAPI.getDatabaseSchema();
    
    expect(schemaResponse).toHaveProperty('db_schema_agent');
    expect(schemaResponse).toHaveProperty('db_schema_user');
    expect(schemaResponse).toHaveProperty('db_path');
    
    // Verify schema contains expected tables
    expect(schemaResponse.db_schema_agent).toContain('FactRegisteredVehicles');
    expect(schemaResponse.db_schema_agent).toContain('DimOEM');
    expect(schemaResponse.db_path).toBe('data/registered_vehicles.sqlite');
    
    console.log('✅ Schema loaded with', schemaResponse.db_path);
  });

  test('Step 0: Orchestration - Intent detection for manufacturer query', async () => {
    const orchestrationResponse = await agentAPI.orchestrateIntent(
      TEST_QUERY,
      JSON.stringify([]),
      JSON.stringify({})
    );
    
    expect(orchestrationResponse).toHaveProperty('success', true);
    expect(orchestrationResponse.data).toHaveProperty('action_type');
    expect(orchestrationResponse.data).toHaveProperty('confidence');
    expect(orchestrationResponse.data).toHaveProperty('reasoning');
    
    // Should detect this as a new query
    expect(orchestrationResponse.data.action_type).toBe('new_query');
    expect(orchestrationResponse.data.confidence).toBeGreaterThan(0.8);
    
    console.log('✅ Orchestration:', {
      action: orchestrationResponse.data.action_type,
      confidence: orchestrationResponse.data.confidence,
      reasoning: orchestrationResponse.data.reasoning
    });
  });

  test('Step 1: SQL Generation - Creates valid manufacturer query', async () => {
    // Get the schema first
    const schemaResponse = await agentAPI.getDatabaseSchema();
    
    const sqlResponse = await agentAPI.generateSQL(
      TEST_QUERY,
      schemaResponse.db_schema_agent
    );
    
    expect(sqlResponse).toHaveProperty('success', true);
    expect(sqlResponse.data).toHaveProperty('sqlquery');
    
    generatedSQL = sqlResponse.data.sqlquery;
    
    // Validate SQL structure for manufacturer query
    expect(generatedSQL).toContain('SELECT');
    expect(generatedSQL).toContain('oem_name');
    expect(generatedSQL).toContain('FactRegisteredVehicles');
    expect(generatedSQL).toContain('DimOEM');
    expect(generatedSQL).toContain('JOIN');
    expect(generatedSQL).toContain('GROUP BY');
    expect(generatedSQL).toContain('ORDER BY');
    
    console.log('✅ Generated SQL:', generatedSQL);
  });

  test('Step 2: SQL Review - Optimizes the generated query', async () => {
    // Use SQL from previous test or generate a new one
    const testSQL = generatedSQL || `
      SELECT o.oem_name, SUM(f.vehicle_count) as total_vehicles
      FROM FactRegisteredVehicles f
      JOIN DimOEM o ON f.oem_key = o.oem_key
      GROUP BY o.oem_name
      ORDER BY total_vehicles DESC;
    `;
    
    const schemaResponse = await agentAPI.getDatabaseSchema();
    const reviewResponse = await agentAPI.reviewSQL(testSQL, schemaResponse.db_schema_agent);
    
    expect(reviewResponse).toHaveProperty('success', true);
    expect(reviewResponse.data).toHaveProperty('reviewed_sqlquery');
    
    reviewedSQL = reviewResponse.data.reviewed_sqlquery;
    
    // Should be a valid SQL query
    expect(reviewedSQL).toContain('SELECT');
    expect(reviewedSQL.length).toBeGreaterThan(0);
    
    console.log('✅ Reviewed SQL:', reviewedSQL);
  });

  test('Step 3: SQL Execution - Retrieves real manufacturer data', async () => {
    // Use reviewed SQL or fallback to a known working query
    const sqlToExecute = reviewedSQL || `
      SELECT o.oem_name, SUM(f.vehicle_count) as total_vehicles
      FROM FactRegisteredVehicles f
      JOIN DimOEM o ON f.oem_key = o.oem_key
      GROUP BY o.oem_name
      ORDER BY total_vehicles DESC
      LIMIT 10;
    `;
    
    const executionResponse = await agentAPI.executeSQL(sqlToExecute);
    
    expect(executionResponse).toHaveProperty('success', true);
    expect(executionResponse.data).toHaveProperty('results');
    expect(executionResponse.data).toHaveProperty('metadata');
    
    queryResults = executionResponse.data.results;
    queryMetadata = executionResponse.data.metadata;
    
    // Validate data structure
    expect(Array.isArray(queryResults)).toBe(true);
    expect(queryResults.length).toBeGreaterThan(0);
    expect(queryMetadata).toHaveProperty('row_count');
    expect(queryMetadata).toHaveProperty('column_count');
    expect(queryMetadata).toHaveProperty('columns');
    
    // Validate manufacturer data structure
    const firstResult = queryResults[0];
    expect(firstResult).toHaveProperty('oem_name');
    expect(firstResult).toHaveProperty('total_vehicles');
    expect(typeof firstResult.total_vehicles).toBe('number');
    expect(firstResult.total_vehicles).toBeGreaterThan(0);
    
    // Validate data is sorted (first should have highest count)
    if (queryResults.length > 1) {
      expect(queryResults[0].total_vehicles).toBeGreaterThanOrEqual(queryResults[1].total_vehicles);
    }
    
    console.log('✅ Query Results:', {
      rowCount: queryMetadata.row_count,
      topManufacturer: queryResults[0],
      sampleData: queryResults.slice(0, 3)
    });
  });

  test('Step 4a: Data Analysis - Analyzes manufacturer data', async () => {
    // Use results from previous test or create sample data
    const testData = queryResults || [
      { oem_name: 'BMW', total_vehicles: 125265 },
      { oem_name: 'AUDI', total_vehicles: 122431 },
      { oem_name: 'MERCEDES-BENZ', total_vehicles: 101969 }
    ];
    
    const analysisResponse = await agentAPI.analyzeData(
      JSON.stringify(testData),
      TEST_QUERY
    );
    
    expect(analysisResponse).toHaveProperty('success', true);
    expect(analysisResponse.data).toHaveProperty('analysis_text');
    
    analysisText = analysisResponse.data.analysis_text;
    
    // Should contain meaningful analysis
    expect(analysisText.length).toBeGreaterThan(50);
    
    console.log('✅ Data Analysis:', analysisText.substring(0, 100) + '...');
  });
    // Store analysis for visualization
    analysisResults = analysisResponse.data;
  });

  test('Step 4b: Visualization Creation - Creates manufacturer chart', async () => {
    const testData = queryResults || [
      { oem_name: 'BMW', total_vehicles: 125265 },
      { oem_name: 'AUDI', total_vehicles: 122431 },
      { oem_name: 'MERCEDES-BENZ', total_vehicles: 101969 }
    ];
    
    const analysis = analysisResults || {
      recommended_visualizations: ['bar_chart'],
      analysis: 'Manufacturer registration data shows clear ranking',
      key_findings: ['BMW leads in registrations']
    };
    
    const vizResponse = await agentAPI.createVisualization(
      JSON.stringify(testData),
      TEST_QUERY
    );
    
    expect(vizResponse).toHaveProperty('success', true);
    expect(vizResponse.data).toHaveProperty('plot_spec');
    
    const plotSpec = JSON.parse(vizResponse.data.plot_spec);
    
    // Validate Plotly specification structure
    expect(plotSpec).toHaveProperty('data');
    expect(plotSpec).toHaveProperty('layout');
    expect(Array.isArray(plotSpec.data)).toBe(true);
    expect(plotSpec.data.length).toBeGreaterThan(0);
    
    // Validate chart data
    const chartData = plotSpec.data[0];
    expect(chartData).toHaveProperty('x');
    expect(chartData).toHaveProperty('y');
    expect(chartData).toHaveProperty('type');
    
    // Validate layout
    expect(plotSpec.layout).toHaveProperty('title');
    expect(plotSpec.layout.title.text).toContain('Manufacturer');
    
    console.log('✅ Visualization Created:', {
      type: chartData.type,
      title: plotSpec.layout.title.text,
      dataPoints: chartData.x.length
    });
  });

  test('Step 4c: Follow-up Questions Generation', async () => {
    const analysis = analysisResults || {
      analysis: 'BMW leads manufacturer registrations',
      key_findings: ['BMW: 125,265 vehicles', 'Audi: 122,431 vehicles']
    };
    
    const schemaResponse = await agentAPI.getDatabaseSchema();
    
    const followUpResponse = await agentAPI.generateFollowUpQuestions(
      analysisText,
      TEST_QUERY
    );
    
    expect(followUpResponse).toHaveProperty('success', true);
    expect(followUpResponse.data).toHaveProperty('questions');
    
    const questions = followUpResponse.data.questions;
    expect(Array.isArray(questions)).toBe(true);
    expect(questions.length).toBeGreaterThan(0);
    
    // Should include relevant follow-up questions
    const questionText = questions.join(' ').toLowerCase();
    expect(
      questionText.includes('region') || 
      questionText.includes('time') || 
      questionText.includes('electric') ||
      questionText.includes('market share')
    ).toBe(true);
    
    console.log('✅ Follow-up Questions:', questions);
  });

  test('Step 5: Alternative Visualization Creation', async () => {
    const testData = queryResults || [
      { oem_name: 'BMW', total_vehicles: 125265 },
      { oem_name: 'AUDI', total_vehicles: 122431 },
      { oem_name: 'MERCEDES-BENZ', total_vehicles: 101969 }
    ];
    
    const altVizResponse = await agentAPI.createAlternativeVisualization(
      JSON.stringify(testData),
      TEST_QUERY
    );
    
    expect(altVizResponse).toHaveProperty('success', true);
    expect(altVizResponse.data).toHaveProperty('plot_spec');
    
    const plotSpec = JSON.parse(altVizResponse.data.plot_spec);
    expect(plotSpec).toHaveProperty('data');
    expect(plotSpec).toHaveProperty('layout');
    
    console.log('✅ Alternative Visualization Created:', {
      type: plotSpec.data[0].type,
      title: plotSpec.layout.title.text
    });
  });

  test('Step 6: Data Question Answering', async () => {
    const testData = queryResults || [
      { oem_name: 'BMW', total_vehicles: 125265 },
      { oem_name: 'AUDI', total_vehicles: 122431 },
      { oem_name: 'MERCEDES-BENZ', total_vehicles: 101969 }
    ];
    
    const dataQuestionResponse = await agentAPI.answerDataQuestion(
      'What is the market share of the top 3 manufacturers?',
      JSON.stringify(testData)
    );
    
    expect(dataQuestionResponse).toHaveProperty('success', true);
    expect(dataQuestionResponse.data).toHaveProperty('answer_text');
    
    const answer = dataQuestionResponse.data.answer_text;
    expect(answer.length).toBeGreaterThan(20);
    
    console.log('✅ Data Question Answered:', answer.substring(0, 100) + '...');
  });

  test('Complete Pipeline Integration - End-to-End Flow', async () => {
    console.log('\n🔄 Running Complete End-to-End Pipeline Test...\n');
    
    // Step 0: Orchestration
    const orchestration = await agentAPI.orchestrateIntent(TEST_QUERY, '[]', '{}');
    expect(orchestration.success).toBe(true);
    console.log('Step 0 ✅ Orchestration:', orchestration.data.action_type);
    
    // Step 1: SQL Generation
    const schema = await agentAPI.getDatabaseSchema();
    const sqlGen = await agentAPI.generateSQL(TEST_QUERY, schema.db_schema_agent);
    expect(sqlGen.success).toBe(true);
    console.log('Step 1 ✅ SQL Generated');
    
    // Step 2: SQL Review
    const sqlReview = await agentAPI.reviewSQL(sqlGen.data.sqlquery, schema.db_schema_agent);
    expect(sqlReview.success).toBe(true);
    console.log('Step 2 ✅ SQL Reviewed');
    
    // Step 3: SQL Execution
    const execution = await agentAPI.executeSQL(sqlReview.data.reviewed_sqlquery);
    expect(execution.success).toBe(true);
    expect(execution.data.results.length).toBeGreaterThan(0);
    console.log('Step 3 ✅ SQL Executed - Retrieved', execution.data.metadata.row_count, 'rows');
    
    // Step 4a: Data Analysis
    const results = execution.data.results;
    const analysis = await agentAPI.analyzeData(
      JSON.stringify(results),
      TEST_QUERY
    );
    expect(analysis.success).toBe(true);
    console.log('Step 4a ✅ Data Analyzed');
    
    // Step 4b: Visualization
    const viz = await agentAPI.createVisualization(
      JSON.stringify(results),
      TEST_QUERY
    );
    expect(viz.success).toBe(true);
    const plotSpec = JSON.parse(viz.data.plot_spec);
    expect(plotSpec.data[0].x.length).toEqual(results.length);
    console.log('Step 4b ✅ Visualization Created');
    
    // Step 4c: Follow-up Questions
    const followUp = await agentAPI.generateFollowUpQuestions(
      analysis.data.analysis_text,
      TEST_QUERY
    );
    expect(followUp.success).toBe(true);
    console.log('Step 4c ✅ Follow-up Questions Generated');
    
    console.log('\n🎉 Complete Pipeline Test PASSED!\n');
    
    // Final validation of data consistency
    const topManufacturer = results[0];
    expect(topManufacturer.oem_name).toBeTruthy();
    expect(topManufacturer.total_vehicles).toBeGreaterThan(0);
    
    console.log('📊 Final Results Summary:');
    console.log('- Top Manufacturer:', topManufacturer.oem_name);
    console.log('- Vehicle Count:', topManufacturer.total_vehicles.toLocaleString());
    console.log('- Total Manufacturers:', results.length);
    console.log('- Visualization Type:', plotSpec.data[0].type);
    console.log('- Follow-up Questions:', followUp.data.questions.length);
  });
});
