# SQL Crew Integration with Review Test

This document describes how to test the SQL crew integration with the two-step generation and review process using AI agents powered by GPT-4o-mini and GPT-4o.

## Test Suite

### Running All Tests

Run the comprehensive test suite to verify all functionality:

```bash
# Run all tests with verbose output
python -m unittest discover tests/ -v

# Alternative: Run tests with summary
cd tests && python -m unittest discover . -v
```

### Test Coverage

The test suite includes 15 tests across 4 modules:

- **Database Tests** (`test_database.py`) - 4 tests
  - Database schema loading
  - SQL query execution
  - Error handling for invalid queries
  
- **SQL Crew Tests** (`test_sql_crew.py`) - 4 tests  
  - Agent import and initialization
  - SQL generation workflow
  - SQL review workflow
  - Complete generation → review pipeline

- **Integration Tests** (`test_integration.py`) - 5 tests
  - End-to-end workflow testing
  - Schema validation
  - SQL syntax verification
  - Multiple query scenarios
  - **Date query SQLite compatibility testing** ⚠️

- **Test Runner** (`test_runner.py`) - 2 tests
  - Test discovery and execution utilities

### Quick Functional Test

For a quick smoke test of the core functionality:

```bash
# Test basic SQL generation (if test file exists)
python test_review_workflow.py
```

## Manual Testing with the App

### Running the App

Start the Streamlit app for interactive testing:

```bash
streamlit run app.py
```

### Interactive Testing Steps

1. **Open the app** - You should see the visualization agent interface
2. **View database schema** - Click on the "📋 View Database Schema" expander to see available tables
3. **Test SQL generation** - Try these sample queries:
   - "Show me all products with their prices"
   - "What are the top 5 most expensive products?"
   - "Count how many customers we have from each country"
   - "Find customers who have made orders over $100"
   - "Show product categories and their average prices"
   - "What are the sales from last month" ⚠️ **(Known Issue - see troubleshooting)**

### Expected Behavior

- **🤖 Initial Generation**: The app will generate SQL queries using GPT-4o-mini
- **🔍 Review Process**: GPT-4o will review and potentially optimize the query
- **✨ Comparison**: If the query is modified, you'll see a side-by-side comparison
- **✅ Approval**: If no changes are needed, the query is approved as-is
- **📊 Execution**: The final reviewed query is executed against the database
- **🎯 Display**: The final SQL query is prominently displayed

## Technical Architecture

### Two-Step AI Process

The app uses a sophisticated two-step SQL generation process:

1. **Step 1: SQL Generation** - GPT-4o-mini generates initial SQL query based on user request
2. **Step 2: SQL Review** - GPT-4o reviews and optimizes the query for correctness and performance

### Agent Configuration

- **Query Generator Agent**: 
  - Model: GPT-4o-mini
  - Role: Senior Data Analyst
  - Task: Translate natural language to SQL using strict schema validation
  
- **Query Reviewer Agent**:
  - Model: GPT-4o  
  - Role: SQL Code Reviewer
  - Task: Review queries for correctness, performance, and readability

- **Schema Enforcement**: Both agents follow strict schema validation to prevent hallucinated tables/columns

### Project Structure

```
tests/
├── test_database.py      # Database utility tests
├── test_sql_crew.py      # SQL crew agent tests  
├── test_integration.py   # End-to-end workflow tests
└── test_runner.py        # Test execution utilities

agents/
├── sql_crew.py          # Agent definitions and crews
└── config/
    ├── agents.yaml      # Agent configurations
    └── tasks.yaml       # Task definitions

utils/
├── db_simulator.py      # Database utilities
└── helper.py           # Helper functions
```

## Database Schema

The sample database contains these tables:
- **products**: product_id, product_name, category, price
- **customers**: customer_id, name, email, country, signup_date  
- **orders**: order_id, customer_id, order_date, total_amount
- **order_items**: order_item_id, order_id, product_id, quantity, price
- **employees**: employee_id, name, department_id, hire_date
- **departments**: department_id, department_name

## Debugging and Troubleshooting

### App Debugging

- Check the "🔍 Debug: Raw Query Result" expander to see raw database output
- Look at the "📊 Query Result" section to see formatted results
- Review the "🔄 SQL Query Comparison" if queries were modified
- Error messages will appear if SQL generation or execution fails

### Test Debugging

```bash
# Run specific test module
python -m unittest tests.test_database -v
python -m unittest tests.test_sql_crew -v
python -m unittest tests.test_integration -v

# Run specific test case
python -m unittest tests.test_sql_crew.TestSQLCrew.test_generation_and_review_workflow -v
```

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed via `poetry install`
2. **Database Errors**: Check that `data/sample_db.sqlite` exists and is accessible
3. **Agent Errors**: Verify API keys are set in environment variables
4. **Test Failures**: Run tests individually to isolate issues

#### Known Issue: Date Queries and Database Compatibility ⚠️

**Problem**: Queries involving dates (e.g., "What are the sales from last month") may fail with syntax errors.

**Root Cause**: The AI agents sometimes generate PostgreSQL-specific date syntax (`DATE_TRUNC`, `INTERVAL`) instead of SQLite-compatible date functions.

**Error Example**:
```
Query failed: near "'1 month'": syntax error
```

**Generated Query (PostgreSQL syntax)**:
```sql
SELECT SUM(o.total_amount) AS total_sales
FROM orders o
WHERE o.order_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
  AND o.order_date < DATE_TRUNC('month', CURRENT_DATE);
```

**SQLite-Compatible Alternative**:
```sql
SELECT SUM(o.total_amount) AS total_sales
FROM orders o
WHERE o.order_date >= date('now', 'start of month', '-1 month')
  AND o.order_date < date('now', 'start of month');
```

**Workaround**: 
- Use simpler date queries like "Show orders from 2024"
- Avoid relative date references like "last month" or "yesterday"
- The test suite includes `test_date_query_sqlite_compatibility` to catch these issues

## Validation Results

✅ **15 tests total** (14 passing + 1 expected failure for date compatibility)  
✅ **Full integration testing** with live AI agent calls  
✅ **Database connectivity** and schema validation  
✅ **SQL generation and review** workflow verification  
✅ **Error handling** and edge case coverage  
⚠️ **Known limitation**: Date queries may use PostgreSQL syntax instead of SQLite
