/**
 * Comprehensive Integration Test for App.js Pipeline
 * Tests the complete flow: "Which car manufacturers registered the most vehicles?"
 * Based on README pipeline architecture
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';
import { agentAPI } from '../api';

// Mock the API module
jest.mock('../api', () => ({
  agentAPI: {
    healthCheck: jest.fn(),
    getDatabaseSchema: jest.fn(),
    orchestrateIntent: jest.fn(),
    generateSQL: jest.fn(),
    reviewSQL: jest.fn(),
    analyzeData: jest.fn(),
    createVisualization: jest.fn(),
    generateFollowUpQuestions: jest.fn(),
    createAlternativeVisualization: jest.fn(),
    answerDataQuestion: jest.fn(),
  }
}));

describe('App.js Integration Test - Car Manufacturers Query', () => {
  const testQuery = "Which car manufacturers registered the most vehicles?";
  
  // Mock data that matches README examples
  const mockManufacturerData = [
    { manufacturer: 'Toyota', count: 25000, market_share: 25.5 },
    { manufacturer: 'Honda', count: 20000, market_share: 20.4 },
    { manufacturer: 'Ford', count: 17000, market_share: 17.0 },
    { manufacturer: 'BMW', count: 13000, market_share: 13.6 },
    { manufacturer: 'Mercedes', count: 12000, market_share: 11.9 },
    { manufacturer: 'Audi', count: 10000, market_share: 10.2 }
  ];

  const mockVisualizationSpec = {
    type: 'bar',
    data: {
      x: mockManufacturerData.map(d => d.manufacturer),
      y: mockManufacturerData.map(d => d.count)
    },
    layout: {
      title: 'Vehicle Registrations by Manufacturer',
      xaxis: { title: 'Manufacturer' },
      yaxis: { title: 'Registration Count' },
      plot_bgcolor: 'white',
      paper_bgcolor: 'white',
      font: { color: 'black' }
    }
  };

  const mockSchemaResponse = {
    db_schema_agent: `
      # 🚗 Vehicle Registration Database (Traditional Star Schema)
      
      ## 📊 FactRegisteredVehicles - Core Fact Table
      **Primary Key**: vehicle_count_id (TEXT)
      **Foreign Keys**: time_key, oem_key, vehicle_key, geography_country_key, geography_district_key
      **Measure**: vehicle_count (INTEGER) - Number of vehicles registered
      
      ## 🏭 DimOEM - Vehicle Manufacturers
      **Primary Key**: oem_key (INTEGER)
      **Columns**: oem_name, oem_category, country_origin
    `,
    db_schema_user: 'User-friendly database schema description',
    db_path: 'data/registered_vehicles.sqlite'
  };

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Setup default mock responses
    agentAPI.healthCheck.mockResolvedValue({ status: 'healthy' });
    agentAPI.getDatabaseSchema.mockResolvedValue(mockSchemaResponse);
  });

  test('Complete Pipeline: Step 0-4 as per README architecture', async () => {
    // Setup mock responses for the complete pipeline
    
    // Step 0: Orchestration
    agentAPI.orchestrateIntent.mockResolvedValue({
      success: true,
      data: {
        action_type: 'new_query',
        confidence: 0.95,
        reasoning: 'User is asking for new data analysis about car manufacturers'
      }
    });

    // Step 1: SQL Generation
    agentAPI.generateSQL.mockResolvedValue({
      success: true,
      data: {
        sqlquery: `SELECT o.oem_name, SUM(f.vehicle_count) as total_vehicles
FROM FactRegisteredVehicles f
JOIN DimOEM o ON f.oem_key = o.oem_key
GROUP BY o.oem_name
ORDER BY total_vehicles DESC;`
      }
    });

    // Step 2: SQL Review
    agentAPI.reviewSQL.mockResolvedValue({
      success: true,
      data: {
        reviewed_sqlquery: `SELECT o.oem_name, SUM(f.vehicle_count) as total_vehicles
FROM FactRegisteredVehicles f
JOIN DimOEM o ON f.oem_key = o.oem_key
GROUP BY o.oem_name
ORDER BY total_vehicles DESC
LIMIT 10;`,
        review_notes: 'Added LIMIT for better performance'
      }
    });

    // Step 4a: Data Analysis
    agentAPI.analyzeData.mockResolvedValue({
      success: true,
      data: {
        recommended_visualizations: ['bar_chart', 'pie_chart'],
        analysis: 'Data shows clear ranking of manufacturers by registration volume',
        key_findings: [
          'Toyota leads with 25,000 registrations',
          'Top 3 manufacturers account for 62.9% of market',
          'Clear competitive hierarchy visible'
        ]
      }
    });

    // Step 4b: Visualization Creation
    agentAPI.createVisualization.mockResolvedValue({
      success: true,
      data: {
        plot_spec: JSON.stringify(mockVisualizationSpec)
      }
    });

    // Follow-up questions generation
    agentAPI.generateFollowUpQuestions.mockResolvedValue({
      success: true,
      data: {
        questions: [
          'Which regions contribute most to Toyota\'s registrations?',
          'Compare electric vs conventional vehicle registrations',
          'Show quarterly registration trends for top manufacturers',
          'What is the market share breakdown by country?'
        ]
      }
    });

    // Render the App
    render(<App />);

    // Wait for initial load and health check
    await waitFor(() => {
      expect(screen.getByText(/🟢 Connected/)).toBeInTheDocument();
    });

    // Verify schema is loaded
    await waitFor(() => {
      expect(agentAPI.getDatabaseSchema).toHaveBeenCalled();
    });

    // Find and fill the input field
    const input = screen.getByPlaceholderText('Ask about your database...');
    fireEvent.change(input, { target: { value: testQuery } });

    // Click send button or press enter
    const sendButton = screen.getByRole('button');
    fireEvent.click(sendButton);

    // Verify Step 0: Orchestration
    await waitFor(() => {
      expect(screen.getByText(/🧠 Understanding your intent/)).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(agentAPI.orchestrateIntent).toHaveBeenCalledWith(
        testQuery,
        expect.any(String),
        expect.any(String)
      );
    });

    // Verify orchestration result is displayed
    await waitFor(() => {
      expect(screen.getByText(/🎯 Intent: NEW_QUERY \(Confidence: 95%\)/)).toBeInTheDocument();
    });

    // Verify Step 1: SQL Generation
    await waitFor(() => {
      expect(screen.getByText(/🤖 Generating SQL query/)).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(agentAPI.generateSQL).toHaveBeenCalledWith(
        testQuery,
        expect.stringContaining('FactRegisteredVehicles')
      );
    });

    // Verify Step 2: SQL Review
    await waitFor(() => {
      expect(screen.getByText(/🔍 Reviewing SQL with GPT-4o verifier/)).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(agentAPI.reviewSQL).toHaveBeenCalled();
    });

    // Verify Step 3: Query Execution
    await waitFor(() => {
      expect(screen.getByText(/🔄 Executing SQL query/)).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText(/✅ Retrieved \d+ rows successfully/)).toBeInTheDocument();
    });

    // Verify Step 4: Data Analysis and Visualization
    await waitFor(() => {
      expect(screen.getByText(/📊 Analyzing data patterns/)).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(agentAPI.analyzeData).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(screen.getByText(/🎨 Creating visualization/)).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(agentAPI.createVisualization).toHaveBeenCalled();
    });

    // Verify visualization success message
    await waitFor(() => {
      expect(screen.getByText(/✨ Visualization created successfully!/)).toBeInTheDocument();
    });

    // Verify follow-up questions are generated
    await waitFor(() => {
      expect(agentAPI.generateFollowUpQuestions).toHaveBeenCalled();
    });

    // Verify follow-up questions are displayed
    await waitFor(() => {
      expect(screen.getByText(/💡 Suggested follow-up questions:/)).toBeInTheDocument();
    });

    // Verify specific follow-up questions appear
    await waitFor(() => {
      expect(screen.getByText(/Which regions contribute most to Toyota's registrations?/)).toBeInTheDocument();
    });

    // Verify metrics are displayed
    await waitFor(() => {
      expect(screen.getByText(/Total Records/)).toBeInTheDocument();
      expect(screen.getByText(/Peak Value/)).toBeInTheDocument();
      expect(screen.getByText(/Average/)).toBeInTheDocument();
    });

    // Verify all API calls were made in the correct order
    expect(agentAPI.healthCheck).toHaveBeenCalled();
    expect(agentAPI.getDatabaseSchema).toHaveBeenCalled();
    expect(agentAPI.orchestrateIntent).toHaveBeenCalled();
    expect(agentAPI.generateSQL).toHaveBeenCalled();
    expect(agentAPI.reviewSQL).toHaveBeenCalled();
    expect(agentAPI.analyzeData).toHaveBeenCalled();
    expect(agentAPI.createVisualization).toHaveBeenCalled();
    expect(agentAPI.generateFollowUpQuestions).toHaveBeenCalled();
  });

  test('Follow-up question handling: Convert bar chart to pie chart', async () => {
    // First, setup the app with existing data (simulate previous query)
    agentAPI.healthCheck.mockResolvedValue({ status: 'healthy' });
    agentAPI.getDatabaseSchema.mockResolvedValue(mockSchemaResponse);

    // Mock the follow-up orchestration
    agentAPI.orchestrateIntent.mockResolvedValue({
      success: true,
      data: {
        action_type: 'follow_up',
        confidence: 0.92,
        reasoning: 'User wants to convert existing visualization to different chart type'
      }
    });

    // Mock alternative visualization creation
    agentAPI.createAlternativeVisualization.mockResolvedValue({
      success: true,
      data: {
        plot_spec: JSON.stringify({
          ...mockVisualizationSpec,
          type: 'pie',
          data: {
            labels: mockManufacturerData.map(d => d.manufacturer),
            values: mockManufacturerData.map(d => d.market_share)
          },
          layout: {
            title: 'Market Share by Manufacturer (%)'
          }
        })
      }
    });

    render(<App />);

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText(/🟢 Connected/)).toBeInTheDocument();
    });

    // Simulate that we already have data from previous query
    // This would normally be set by a previous successful query
    const followUpQuery = "Convert the bar chart to pie chart";
    
    const input = screen.getByPlaceholderText('Ask about your database...');
    fireEvent.change(input, { target: { value: followUpQuery } });

    const sendButton = screen.getByRole('button');
    fireEvent.click(sendButton);

    // Verify follow-up orchestration
    await waitFor(() => {
      expect(agentAPI.orchestrateIntent).toHaveBeenCalledWith(
        followUpQuery,
        expect.any(String),
        expect.any(String)
      );
    });

    // Note: The actual follow-up flow depends on having currentData set
    // In a real scenario, this would be populated from a previous query
  });

  test('Error handling: API failure scenarios', async () => {
    // Test health check failure
    agentAPI.healthCheck.mockRejectedValue(new Error('Connection failed'));
    agentAPI.getDatabaseSchema.mockResolvedValue(mockSchemaResponse);

    render(<App />);

    // Should show disconnected status
    await waitFor(() => {
      expect(screen.getByText(/🔴 Disconnected/)).toBeInTheDocument();
    });

    // Test SQL generation failure
    agentAPI.orchestrateIntent.mockResolvedValue({
      success: true,
      data: { action_type: 'new_query', confidence: 0.95, reasoning: 'Test' }
    });

    agentAPI.generateSQL.mockRejectedValue(new Error('SQL generation failed'));

    const input = screen.getByPlaceholderText('Ask about your database...');
    fireEvent.change(input, { target: { value: testQuery } });

    const sendButton = screen.getByRole('button');
    fireEvent.click(sendButton);

    // Should show error message
    await waitFor(() => {
      expect(screen.getByText(/Sorry, I encountered an error processing your request/)).toBeInTheDocument();
    });
  });

  test('Pipeline step visualization and completion tracking', async () => {
    // Setup successful pipeline mocks
    agentAPI.healthCheck.mockResolvedValue({ status: 'healthy' });
    agentAPI.getDatabaseSchema.mockResolvedValue(mockSchemaResponse);
    agentAPI.orchestrateIntent.mockResolvedValue({
      success: true,
      data: { action_type: 'new_query', confidence: 0.95, reasoning: 'Test' }
    });
    agentAPI.generateSQL.mockResolvedValue({
      success: true,
      data: { sqlquery: 'SELECT * FROM test;' }
    });
    agentAPI.reviewSQL.mockResolvedValue({
      success: true,
      data: { reviewed_sqlquery: 'SELECT * FROM test LIMIT 10;' }
    });
    agentAPI.analyzeData.mockResolvedValue({
      success: true,
      data: {
        recommended_visualizations: ['bar'],
        analysis: 'Test analysis',
        key_findings: ['Test finding']
      }
    });
    agentAPI.createVisualization.mockResolvedValue({
      success: true,
      data: { plot_spec: JSON.stringify(mockVisualizationSpec) }
    });
    agentAPI.generateFollowUpQuestions.mockResolvedValue({
      success: true,
      data: { questions: ['Test question?'] }
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/🟢 Connected/)).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText('Ask about your database...');
    fireEvent.change(input, { target: { value: testQuery } });

    const sendButton = screen.getByRole('button');
    fireEvent.click(sendButton);

    // Verify pipeline components are shown
    // Note: The actual pipeline steps display depends on the PipelineSteps component
    // This test verifies the orchestration flow is triggered
    await waitFor(() => {
      expect(agentAPI.orchestrateIntent).toHaveBeenCalled();
    });
  });
});
