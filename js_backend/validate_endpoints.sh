#!/bin/bash

# Test all FastAPI endpoints
# This script validates that every endpoint is working properly

echo "🧪 FastAPI Backend Endpoint Validation"
echo "======================================"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

# Check if the backend is running
echo "📡 Checking backend health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not responding. Please start with 'docker-compose up'"
    exit 1
fi

# Function to test an endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local payload=$3
    local expected_status=$4
    local description=$5
    
    echo -n "Testing $description... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" "http://localhost:8000$endpoint")
    else
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$payload" "http://localhost:8000$endpoint")
    fi
    
    http_status=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    body=$(echo "$response" | sed 's/HTTPSTATUS:[0-9]*$//')
    
    if [[ "$expected_status" == *"$http_status"* ]]; then
        echo "✅ ($http_status)"
        return 0
    else
        echo "❌ ($http_status) - Expected: $expected_status"
        echo "   Response: $body"
        return 1
    fi
}

# Test counters
passed=0
failed=0

# Basic endpoints
echo -e "\n📋 Testing Basic Endpoints:"

test_endpoint "GET" "/" "" "200" "Root endpoint"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi

test_endpoint "GET" "/health" "" "200" "Health check"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi

test_endpoint "GET" "/config/schema" "" "200" "Config schema"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi

test_endpoint "GET" "/agents/list" "" "200" "Agents list"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi

# SQL endpoints
echo -e "\n🔍 Testing SQL Endpoints:"

sql_gen_payload='{"user_input": "Show me all registered vehicles", "db_schema": "test schema"}'
test_endpoint "POST" "/agents/sql-generator" "$sql_gen_payload" "200 503" "SQL Generator"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi

sql_review_payload='{"sql_query": "SELECT * FROM vehicles;", "db_schema": "test schema"}'
test_endpoint "POST" "/agents/sql-reviewer" "$sql_review_payload" "200 503" "SQL Reviewer"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi

sql_exec_payload='{"sql_query": "SELECT * FROM nonexistent_table;"}'
test_endpoint "POST" "/agents/execute-sql" "$sql_exec_payload" "404 500" "SQL Executor (missing DB)"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi

# Data Analysis endpoints
echo -e "\n📊 Testing Data Analysis Endpoints:"

analysis_payload='{"columns": "id,name,count", "shape": "100x3", "dtypes": "int,str,int", "sample_data": "{\"id\": 1, \"name\": \"test\", \"count\": 10}", "user_query": "Analyze vehicle data"}'
test_endpoint "POST" "/agents/data-analysis" "$analysis_payload" "200 503" "Data Analysis"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi

viz_payload='{"data": "{\"name\": [\"BMW\", \"Audi\"], \"count\": [100, 80]}", "user_query": "Create a chart", "recommended_viz": "bar chart", "analysis": "Vehicle counts by manufacturer", "key_findings": "BMW has highest count"}'
test_endpoint "POST" "/agents/data-visualization" "$viz_payload" "200 503" "Data Visualization"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi

# Interaction endpoints
echo -e "\n💬 Testing Interaction Endpoints:"

orchestration_payload='{"user_input": "Which car manufacturers registered the most vehicles?", "previous_context": ""}'
test_endpoint "POST" "/agents/orchestration" "$orchestration_payload" "200 503" "Orchestration"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi

question_payload='{"user_question": "What does this chart show?", "current_data": "{\"values\": [1, 2, 3]}", "data_summary": "Vehicle registration data", "chart_info": "Bar chart showing counts"}'
test_endpoint "POST" "/agents/data-question" "$question_payload" "200 503" "Data Question"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi

alt_viz_payload='{"user_request": "Show this as a pie chart", "current_data": "{\"category\": [\"A\", \"B\"], \"value\": [1, 2]}", "current_chart_type": "bar"}'
test_endpoint "POST" "/agents/alternative-visualization" "$alt_viz_payload" "200 503" "Alternative Visualization"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi

followup_payload='{"analysis": "Vehicle data analysis", "original_query": "Show vehicle counts", "key_findings": "BMW leads registrations", "db_schema": "vehicle registration schema"}'
test_endpoint "POST" "/agents/follow-up-questions" "$followup_payload" "200 503" "Follow-up Questions"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi

# Error handling tests
echo -e "\n⚠️  Testing Error Handling:"

# Missing required field
invalid_payload='{"user_input": "test query"}'
test_endpoint "POST" "/agents/sql-generator" "$invalid_payload" "422" "Validation Error (missing db_schema)"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi

# Missing user_input for orchestration
invalid_orchestration='{"previous_context": "some context"}'
test_endpoint "POST" "/agents/orchestration" "$invalid_orchestration" "400 503" "Orchestration Error (missing user_input)"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi

# Summary
echo -e "\n📊 Test Results Summary:"
echo "======================================"
echo "✅ Passed: $passed"
echo "❌ Failed: $failed"
echo "📈 Total:  $((passed + failed))"

if [ $failed -eq 0 ]; then
    echo -e "\n🎉 All tests passed! Your FastAPI backend is working correctly."
    exit 0
else
    echo -e "\n💥 Some tests failed. Please check the endpoint implementations."
    exit 1
fi
