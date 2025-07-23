# SQL Crew Integration Test

This document describes how to test the SQL crew integration in the app.

## Quick Test

Run the test workflow to verify SQL generation works:

```bash
python test_workflow.py
```

## Running the App

Start the Streamlit app:

```bash
streamlit run app.py
```

## Testing Steps

1. **Open the app** - You should see the visualization agent interface
2. **View database schema** - Click on the "📋 View Database Schema" expander to see available tables
3. **Test SQL generation** - Try these sample queries:
   - "Show me all products with their prices"
   - "Count total number of customers" 
   - "What are the top 3 most expensive products?"

## What to Expect

- The app will generate SQL queries using the CrewAI agent
- The generated SQL will be displayed in the interface
- Query results will be shown as formatted text
- If Plotly is not installed, charts will be disabled but SQL generation still works

## Database Schema

The sample database contains these tables:
- **products**: product_id, product_name, category, price
- **customers**: customer_id, name, email, country, signup_date  
- **orders**: order_id, customer_id, order_date, total_amount
- **order_items**: order_item_id, order_id, product_id, quantity, price
- **employees**: employee_id, name, department_id, hire_date
- **departments**: department_id, department_name

## Debugging

- Check the "🔍 Debug: Raw Query Result" expander to see raw database output
- Look at the "📊 Query Result" section to see formatted results
- Error messages will appear if SQL generation or execution fails
