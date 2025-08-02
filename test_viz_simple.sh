#!/bin/bash

# Simple Visualization Test Script
set -e

echo "🎨 Testing Visualization Pipeline"
echo "================================"

BACKEND_URL="http://localhost:8000"

# Test Data
TEST_DATA='[{"oem_name":"BMW","total_vehicles":150},{"oem_name":"AUDI","total_vehicles":120},{"oem_name":"MERCEDES-BENZ","total_vehicles":100}]'

echo "📊 Testing Data Visualization Endpoint"
echo "-------------------------------------"

# Create the payload with correct types
VIZ_PAYLOAD='{
  "data": "'"$(echo $TEST_DATA | sed 's/"/\\"/g')"'",
  "user_query": "Which car manufacturers registered the most vehicles?",
  "recommended_viz": "bar",
  "analysis": "BMW has the highest vehicle registrations, followed by AUDI and MERCEDES-BENZ.",
  "key_findings": "BMW leads with 150 vehicles, AUDI follows with 120, and MERCEDES-BENZ has 100."
}'

echo "📤 Sending request to $BACKEND_URL/agents/data-visualization"

# Make the request
RESPONSE=$(curl -s -X POST $BACKEND_URL/agents/data-visualization \
  -H "Content-Type: application/json" \
  -d "$VIZ_PAYLOAD")

echo "📥 Response received:"
echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"

# Check if successful
SUCCESS=$(echo "$RESPONSE" | jq -r '.success' 2>/dev/null || echo "false")

if [ "$SUCCESS" = "true" ]; then
    echo ""
    echo "✅ SUCCESS! Visualization endpoint is working"
    
    # Extract and validate plot spec
    PLOT_SPEC=$(echo "$RESPONSE" | jq -r '.data.plot_spec' 2>/dev/null)
    if [ "$PLOT_SPEC" != "null" ] && [ "$PLOT_SPEC" != "" ]; then
        echo ""
        echo "📋 Plot Specification Analysis:"
        echo "------------------------------"
        
        # Parse plot spec details
        PLOT_TYPE=$(echo "$PLOT_SPEC" | jq -r '.type' 2>/dev/null || echo "unknown")
        X_DATA=$(echo "$PLOT_SPEC" | jq -r '.data.x' 2>/dev/null || echo "[]")
        Y_DATA=$(echo "$PLOT_SPEC" | jq -r '.data.y' 2>/dev/null || echo "[]")
        TITLE=$(echo "$PLOT_SPEC" | jq -r '.layout.title' 2>/dev/null || echo "No title")
        
        echo "🔹 Chart Type: $PLOT_TYPE"
        echo "🔹 Title: $TITLE"
        echo "🔹 X Data: $X_DATA"
        echo "🔹 Y Data: $Y_DATA"
        
        # Save for debugging
        echo "$PLOT_SPEC" > /tmp/working_plot_spec.json
        echo ""
        echo "💾 Saved plot spec to /tmp/working_plot_spec.json"
        
        echo ""
        echo "🎯 READY FOR FRONTEND TEST!"
        echo "============================="
        echo "1. Open http://localhost:3000"
        echo "2. Ask: 'Which car manufacturers registered the most vehicles?'"
        echo "3. The visualization should now render correctly!"
        
    else
        echo "❌ Plot specification is missing or invalid"
        exit 1
    fi
else
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error' 2>/dev/null || echo "Unknown error")
    echo ""
    echo "❌ FAILED! Error: $ERROR_MSG"
    exit 1
fi

echo ""
echo "🔍 Test completed successfully!"
