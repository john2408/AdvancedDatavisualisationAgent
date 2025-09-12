# SQL Agent Accuracy Evaluation System

This system evaluates the accuracy of the SQL generation agents by comparing their output with expected results from a comprehensive test dataset.

## Overview

The evaluation system tests the complete SQL generation pipeline:

1. **Step 1**: Generate SQL query using `sql_generator_crew`
2. **Step 2**: Review and refine SQL using `sql_reviewer_crew` 
3. **Step 3**: Execute query using `run_query`

The results are compared against a baseline dataset (`complete_test_data.json`) containing 24 pre-generated questions with expected outcomes.

## Scoring System

For each question, the system awards points based on:

- **Rows Match (50 points)**: Actual number of rows equals expected number of rows
- **Columns Count Match (40 points)**: Actual number of columns equals expected number of columns  
- **Column Names Match (10 points)**: Actual column names exactly match expected column names

**Maximum Score**: 100 points per question

## Files Structure

```
tests/
├── test_evaluate_sql_agent_accuracy.py  # Main evaluation logic
├── test_data/
│   ├── generated/
│   │   └── complete_test_data.json      # Expected results (24 questions)
│   ├── sample_sql_questions.py          # Test questions list
│   └── evaluation_results/              # Output directory for results
│       └── sql_agent_evaluation_*.json  # Timestamped evaluation results
    ├── quick_eval_test.py               # Quick test of scoring logic
    └── run_evaluation.py                # Command line runner
```

## Usage

### Quick Test (Scoring Logic Only)
```bash
python run_evaluation.py --quick-test
```

### Evaluate First 3 Questions
```bash
python run_evaluation.py --max-questions 3
```

### Full Evaluation (All 24 Questions)
```bash
python run_evaluation.py
```

### Run Without Saving Results
```bash
python run_evaluation.py --no-save
```

### Direct Python Usage
```python
from tests.test_evaluate_sql_agent_accuracy import SQLAgentEvaluator

evaluator = SQLAgentEvaluator()

# Evaluate single question
result = evaluator.evaluate_question(6, "What are the top 5 car brands by total registrations in 2024?")

# Evaluate all questions
results = evaluator.evaluate_all_questions(max_questions=5)
```

## Expected Test Data Structure

The `complete_test_data.json` file contains baseline results with this structure:

```json
{
  "Question1": {
    "Question": "What are the monthly registration trends for BMW, AUDI, and MERCEDES-BENZ by body type since 2023?",
    "SQL_Query": "SELECT t.year_month, v.body_type, SUM(f.vehicle_count) as total_registrations...",
    "Dataframe": [...],
    "Rows": 168,
    "Columns": ["year_month", "body_type", "total_registrations"],
    "Generated_At": "2025-09-06T16:35:54.197191",
    "Success": true,
    "Attempts": 1
  },
  ...
}
```

## Evaluation Results

Results are saved as timestamped JSON files containing:

```json
{
  "summary": {
    "total_questions": 24,
    "successful_evaluations": 23,
    "failed_evaluations": 1,
    "overall_accuracy_percent": 95.83,
    "average_score_per_question": 87.5
  },
  "results": {
    "Question1": {
      "question_num": 1,
      "question": "...",
      "expected": {...},
      "actual": {...},
      "comparison": {...},
      "score": 100,
      "max_score": 100
    },
    ...
  }
}
```

## Test Questions Coverage

The evaluation covers 24 diverse SQL scenarios:

1. **Time Series Analysis** (Questions 1-7)
   - Monthly trends by brand and body type
   - Electric vehicle registrations over time
   - Fuel type comparisons
   - Total registration trends

2. **Year-over-Year Comparisons** (Questions 8-17)
   - Electric vehicle growth
   - SUV registration changes
   - Quarterly comparisons by brand
   - Growth rates by fuel type and body type

3. **Geographic Analysis** (Questions 18-24)
   - Country-level registrations
   - Regional preferences
   - District-level electric vehicle adoption
   - Brand preferences by region

## Performance Expectations

- **Individual Question**: ~30-60 seconds (includes SQL generation, review, and execution)
- **3 Questions**: ~2-3 minutes
- **Full Evaluation (24 questions)**: ~15-30 minutes

Time varies based on:
- CrewAI agent response times
- Database query complexity
- Network connectivity to OpenAI API

## Error Handling

The system includes robust error handling for:
- Network timeouts during agent execution
- SQL execution errors
- Malformed responses from agents
- Database connectivity issues

Failed evaluations are recorded with error details and contribute 0 points to the overall score.

## Interpreting Results

### Score Ranges
- **90-100**: Excellent accuracy, agents consistently generate correct queries
- **70-89**: Good accuracy, minor issues with column naming or result structure  
- **50-69**: Moderate accuracy, some fundamental issues with query logic
- **Below 50**: Poor accuracy, significant problems requiring investigation

### Common Issues
- **Row count mismatches**: Often indicate filtering or aggregation logic errors
- **Column count differences**: May suggest missing JOINs or incorrect GROUP BY clauses
- **Column name mismatches**: Usually aliasing issues or incorrect table references

## Extending the System

To add new test questions:

1. Add question to `tests/test_data/sample_sql_questions.py`
2. Generate expected results using `complete_test_generator.py`
3. Update the evaluation logic if needed

The system is designed to be extensible for different database schemas and question types.
