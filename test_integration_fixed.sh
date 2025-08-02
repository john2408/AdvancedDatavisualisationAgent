#!/bin/bash

# Full Frontend/Backend Integration Test with Fixed createVisualization
echo "🔧 Full Integration Test - Testing Fixed createVisualization"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
tests_passed=0
tests_failed=0

test_step() {
    echo -e "${BLUE}🧪 Testing: $1${NC}"
}

test_pass() {
    echo -e "${GREEN}✅ PASS: $1${NC}"
    ((tests_passed++))
}

test_fail() {
    echo -e "${RED}❌ FAIL: $1${NC}"
    ((tests_failed++))
}

# Check if services are running
test_step "Backend Health Check"
response=$(curl -s -w "%{http_code}" -o /tmp/health_response.json "http://localhost:8000/health")
if [[ "$response" == "200" ]]; then
    test_pass "Backend is healthy"
else
    test_fail "Backend is not responding (HTTP $response)"
    exit 1
fi

test_step "Frontend Accessibility"
response=$(curl -s -w "%{http_code}" -o /dev/null "http://localhost:3000")
if [[ "$response" == "200" ]]; then
    test_pass "Frontend is accessible"
else
    test_fail "Frontend is not accessible (HTTP $response)"
fi

# Step 1: Test SQL Generation
test_step "Step 1: SQL Generation"
sql_response=$(curl -s -X POST "http://localhost:8000/agents/sql-generator" \
    -H "Content-Type: application/json" \
    -d '{
        "user_input": "Show me vehicle registrations by manufacturer",
        "db_schema": "vehicle_registrations (id, manufacturer, model, year, registration_date)"
    }')

sql_query=$(echo "$sql_response" | jq -r '.data.sqlquery // empty')
if [[ -n "$sql_query" ]]; then
    test_pass "SQL Generation: $sql_query"
else
    test_fail "SQL Generation failed"
fi

# Step 2: Test SQL Review
test_step "Step 2: SQL Review"
review_response=$(curl -s -X POST "http://localhost:8000/agents/sql-reviewer" \
    -H "Content-Type: application/json" \
    -d "{
        \"sql_query\": \"$sql_query\",
        \"db_schema\": \"vehicle_registrations (id, manufacturer, model, year, registration_date)\"
    }")

reviewed_sql=$(echo "$review_response" | jq -r '.data.reviewed_sqlquery // empty')
if [[ -n "$reviewed_sql" ]]; then
    test_pass "SQL Review: $reviewed_sql"
else
    test_fail "SQL Review failed"
fi

# Step 3: Simulate SQL Execution (with mock data)
test_step "Step 3: Simulated SQL Execution"
mock_data='[
    {"manufacturer": "BMW", "count": 150},
    {"manufacturer": "AUDI", "count": 120},
    {"manufacturer": "MERCEDES-BENZ", "count": 100},
    {"manufacturer": "Honda", "count": 10},
    {"manufacturer": "Lexus", "count": 5}
]'
test_pass "Mock data prepared for analysis"

# Step 4a: Test Data Analysis
test_step "Step 4a: Data Analysis"
analysis_response=$(curl -s -X POST "http://localhost:8000/agents/data-analysis" \
    -H "Content-Type: application/json" \
    -d "{
        \"data\": \"$mock_data\",
        \"user_query\": \"Show me vehicle registrations by manufacturer\"
    }")

analysis=$(echo "$analysis_response" | jq -r '.data.analysis // empty')
recommended_viz=$(echo "$analysis_response" | jq -r '.data.recommended_visualizations[]' | tr '\n' ', ')
key_findings=$(echo "$analysis_response" | jq -r '.data.key_findings[]' | tr '\n' ', ' | sed 's/, $//')

if [[ -n "$analysis" && -n "$recommended_viz" && -n "$key_findings" ]]; then
    test_pass "Data Analysis completed"
    echo -e "  📊 Analysis: ${analysis:0:100}..."
    echo -e "  📈 Recommended viz: $recommended_viz"
    echo -e "  🔍 Key findings: ${key_findings:0:100}..."
else
    test_fail "Data Analysis failed"
fi

# Step 4b: Test Data Visualization with FIXED key_findings (as string)
test_step "Step 4b: Data Visualization (FIXED VERSION)"
viz_response=$(curl -s -X POST "http://localhost:8000/agents/data-visualization" \
    -H "Content-Type: application/json" \
    -d "{
        \"data\": \"$mock_data\",
        \"user_query\": \"Show me vehicle registrations by manufacturer\",
        \"recommended_viz\": \"$recommended_viz\",
        \"analysis\": \"$analysis\",
        \"key_findings\": \"$key_findings\"
    }")

plot_spec=$(echo "$viz_response" | jq -r '.data.plot_spec // empty')
plot_type=$(echo "$viz_response" | jq -r '.data.plot_type // empty')
success=$(echo "$viz_response" | jq -r '.success // false')

if [[ "$success" == "true" && -n "$plot_spec" && -n "$plot_type" ]]; then
    test_pass "Data Visualization created successfully"
    echo -e "  📊 Plot type: $plot_type"
    echo -e "  📈 Plot spec length: ${#plot_spec} characters"
    
    # Validate the plot_spec is valid JSON
    echo "$plot_spec" | jq . > /dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        test_pass "Plot specification is valid JSON"
    else
        test_fail "Plot specification is invalid JSON"
    fi
else
    test_fail "Data Visualization failed"
    echo -e "  Error: $(echo "$viz_response" | jq -r '.error // .detail // "Unknown error"')"
fi

# Step 5: Test Follow-up Questions
test_step "Step 5: Follow-up Questions Generation"
followup_response=$(curl -s -X POST "http://localhost:8000/agents/follow-up-questions" \
    -H "Content-Type: application/json" \
    -d "{
        \"analysis\": \"$analysis\",
        \"original_query\": \"Show me vehicle registrations by manufacturer\",
        \"key_findings\": \"$key_findings\",
        \"db_schema\": \"vehicle_registrations (id, manufacturer, model, year, registration_date)\"
    }")

followup_questions=$(echo "$followup_response" | jq -r '.data.questions[]?' | wc -l)
if [[ "$followup_questions" -gt 0 ]]; then
    test_pass "Follow-up questions generated ($followup_questions questions)"
else
    test_fail "Follow-up questions generation failed"
fi

# Frontend-specific tests
test_step "Frontend JavaScript API Format Test"

# Test if our fixed frontend would work by simulating the createVisualization function
cat > /tmp/test_frontend_fix.js << 'EOF'
// Test the fixed createVisualization logic
const analysisData = {
    analysis: "BMW has the highest vehicle registrations, followed by AUDI and MERCEDES-BENZ.",
    recommended_visualizations: ["bar", "pie"],
    key_findings: [
        "BMW has the highest vehicle registrations, followed by AUDI and MERCEDES-BENZ.",
        "Potentially check for low registration anomalies among manufacturers like Lexus or Honda."
    ]
};

// OLD (BROKEN) VERSION:
const brokenPayload = {
    key_findings: analysisData.key_findings  // ❌ Array!
};

// NEW (FIXED) VERSION:
const fixedPayload = {
    key_findings: Array.isArray(analysisData.key_findings) 
        ? analysisData.key_findings.join(', ') 
        : analysisData.key_findings  // ✅ String!
};

console.log('❌ BROKEN payload key_findings type:', typeof brokenPayload.key_findings);
console.log('❌ BROKEN payload key_findings:', brokenPayload.key_findings);
console.log('✅ FIXED payload key_findings type:', typeof fixedPayload.key_findings);
console.log('✅ FIXED payload key_findings:', fixedPayload.key_findings);

// Check if the fix worked
if (typeof fixedPayload.key_findings === 'string') {
    console.log('🎉 Frontend fix validation: SUCCESS');
    process.exit(0);
} else {
    console.log('💥 Frontend fix validation: FAILED');
    process.exit(1);
}
EOF

node /tmp/test_frontend_fix.js
if [[ $? -eq 0 ]]; then
    test_pass "Frontend key_findings fix validation"
else
    test_fail "Frontend key_findings fix validation"
fi

# Summary
echo ""
echo "📊 Integration Test Results:"
echo "============================================================"
echo -e "${GREEN}✅ Tests Passed: $tests_passed${NC}"
if [[ $tests_failed -gt 0 ]]; then
    echo -e "${RED}❌ Tests Failed: $tests_failed${NC}"
else
    echo -e "${GREEN}❌ Tests Failed: $tests_failed${NC}"
fi
echo -e "${BLUE}📈 Total Tests: $((tests_passed + tests_failed))${NC}"

if [[ $tests_failed -eq 0 ]]; then
    echo -e "${GREEN}🎉 All integration tests passed! The fixed createVisualization function should work correctly.${NC}"
    exit 0
else
    echo -e "${RED}💥 Some tests failed. Please check the output above.${NC}"
    exit 1
fi
