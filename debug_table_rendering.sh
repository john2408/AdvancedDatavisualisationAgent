#!/bin/bash

echo "🔍 Testing Frontend renderDataTable Debug"
echo "==========================================="

# First, let's test that the backend is working properly
echo "Step 1: Testing backend SQL execution..."
RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d '{"sql_query": "SELECT o.oem_name, SUM(f.vehicle_count) as total_count FROM FactRegisteredVehicles f JOIN DimOEM o ON f.oem_key = o.oem_key GROUP BY o.oem_name ORDER BY total_count DESC LIMIT 3"}' "http://localhost:8000/agents/execute-sql")

echo "Backend response structure:"
echo "$RESPONSE" | jq '{success: .success, data_exists: (.data != null), results_count: (.data.results | length)}'

if echo "$RESPONSE" | jq -e '.success == true' > /dev/null 2>&1; then
    echo "✅ Backend SQL execution works"
    
    SAMPLE_DATA=$(echo "$RESPONSE" | jq -c '.data.results[0]')
    echo "Sample data structure: $SAMPLE_DATA"
    
    echo ""
    echo "Step 2: Now check frontend..."
    echo "🌐 Open http://localhost:3000 in your browser"
    echo "📝 Try asking: 'Show me the top car manufacturers'"
    echo ""
    echo "🐛 Look for DEBUG INFO in the UI and console logs:"
    echo "   - Check browser developer console (F12)"
    echo "   - Look for blue DEBUG INFO box in the UI"
    echo "   - Watch for renderDataTable logs"
    echo ""
    echo "Expected flow:"
    echo "1. currentData should be set after SQL execution"
    echo "2. DEBUG INFO box should show currentData exists: YES"
    echo "3. renderDataTable function should be called with data"
    echo "4. Table should render below the debug info"
    
else
    echo "❌ Backend SQL execution failed"
    echo "Response: $RESPONSE"
fi
