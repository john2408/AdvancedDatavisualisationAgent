# SQL Agent Robustness Evaluation Report

**Generated on:** 2025-09-09 22:26:25  
**Evaluation Duration:** 1803.69 seconds  
**Questions Evaluated:** 24  
**Runs per Question:** 10  
**Total Runs Executed:** 240  
**Total Successful Runs:** 238  

## Executive Summary

This report evaluates the robustness and consistency of the SQL agent by running each question multiple times and analyzing the variance in results. The evaluation measures three key scoring components:

1. **Rows Score** (50 points): Accuracy of the number of rows returned
2. **Columns Count Score** (40 points): Correctness of the number of columns
3. **Column Names Score** (10 points): Exact match of column names

## Overall Performance Metrics

### Success Rate Analysis
- **Overall Success Rate**: 99.17%
- **Questions with at least one successful run**: 24/24
- **Questions with zero successful runs**: 0/24
- **Average Score Across Questions**: 86.84/100

### Robustness Metrics

#### Global Statistics (Successful Runs Only)

| Metric | Mean | Median | Std Dev | Min | Max | Count |
|--------|------|--------|---------|-----|-----|-------|
| **Rows Score** | 41.39 | 50.00 | 18.92 | 0 | 50 | 238 |
| **Columns Count Score** | 38.66 | 40.00 | 7.22 | 0 | 40 | 238 |
| **Column Names Score** | 6.76 | 10.00 | 4.69 | 0 | 10 | 238 |
| **Total Score** | 86.81 | 100.00 | 21.64 | 0 | 100 | 238 |

## Question-by-Question Analysis

### Performance Categories

- **High Variance Questions** (std > 10): 14 questions
- **Consistent Questions** (std < 5, success > 80%): 10 questions

#### High Variance Questions

| Question | Std Dev | Success Rate |
|----------|---------|-------------|
| Q5 | 30.00 | 100.0% |
| Q4 | 28.72 | 100.0% |
| Q20 | 27.00 | 100.0% |
| Q1 | 24.49 | 100.0% |
| Q7 | 22.91 | 100.0% |

#### Most Consistent Questions

| Question | Std Dev | Success Rate |
|----------|---------|-------------|
| Q6 | 0.00 | 100.0% |
| Q8 | 0.00 | 100.0% |
| Q14 | 0.00 | 100.0% |
| Q18 | 0.00 | 100.0% |
| Q22 | 0.00 | 100.0% |

## Score Distribution Analysis

### Perfect Score Analysis (out of 238 successful runs)

- **Perfect Rows Score (50/50)**: 197 runs (82.8%)
- **Perfect Columns Count Score (40/40)**: 230 runs (96.6%)
- **Perfect Column Names Score (10/10)**: 161 runs (67.6%)
- **Perfect Total Score (100/100)**: 139 runs (58.4%)

## Variance Analysis

### Standard Deviation Summary Across All Questions

| Score Component | Mean Std | Max Std | Questions with Std > 5 |
|-----------------|----------|---------|------------------------|
| Total Score | 12.52 | 30.00 | 14 |
| Rows Score | 7.16 | 25.00 | 8 |
| Columns Count Score | 3.72 | 16.00 | 7 |
| Column Names Score | 2.07 | 5.00 | 0 |

## Detailed Results Summary

| Q# | Question | Runs | Success Rate | Total Score (μ±σ) | Rows Score (μ±σ) | Cols Count (μ±σ) | Col Names (μ±σ) |
|----|----------|------|--------------|-------------------|------------------|------------------|------------------|
| 1 | What are the monthly registrat... | 10 | 100.0% | 80.0±24.5 | 30.0±24.5 | 40.0±0.0 | 10.0±0.0 |
| 2 | What are the monthly registrat... | 10 | 100.0% | 89.0±19.7 | 40.0±20.0 | 40.0±0.0 | 9.0±3.0 |
| 3 | Provide a comparison of monthl... | 10 | 100.0% | 60.0±20.0 | 10.0±20.0 | 40.0±0.0 | 10.0±0.0 |
| 4 | Provide a comparison of monthl... | 10 | 100.0% | 65.0±28.7 | 20.0±24.5 | 40.0±0.0 | 5.0±5.0 |
| 5 | Monthly registrations for ELEC... | 10 | 100.0% | 70.0±30.0 | 25.0±25.0 | 40.0±0.0 | 5.0±5.0 |
| 6 | What are the top 5 car brands ... | 10 | 100.0% | 100.0±0.0 | 50.0±0.0 | 40.0±0.0 | 10.0±0.0 |
| 7 | What are the monthly registrat... | 10 | 100.0% | 65.0±22.9 | 15.0±22.9 | 40.0±0.0 | 10.0±0.0 |
| 8 | What are the year-over-year gr... | 10 | 100.0% | 100.0±0.0 | 50.0±0.0 | 40.0±0.0 | 10.0±0.0 |
| 9 | Year-over-year comparison of S... | 10 | 100.0% | 99.0±3.0 | 50.0±0.0 | 40.0±0.0 | 9.0±3.0 |
| 10 | Q1 2024 vs Q1 2023 comparison ... | 10 | 100.0% | 90.0±20.0 | 50.0±0.0 | 32.0±16.0 | 8.0±4.0 |
| 11 | Q1 2024 vs Q1 2023 comparison ... | 10 | 100.0% | 95.0±15.0 | 50.0±0.0 | 36.0±12.0 | 9.0±3.0 |
| 12 | Q1 2024 vs Q1 2023 comparison ... | 10 | 100.0% | 94.0±15.0 | 50.0±0.0 | 36.0±12.0 | 8.0±4.0 |
| 13 | Q1 2024 vs Q1 2023 comparison ... | 10 | 100.0% | 94.0±15.0 | 50.0±0.0 | 36.0±12.0 | 8.0±4.0 |
| 14 | What are the top 3 body types ... | 10 | 100.0% | 90.0±0.0 | 50.0±0.0 | 40.0±0.0 | 0.0±0.0 |
| 15 | Show me a waterfall chart of y... | 10 | 100.0% | 94.0±4.9 | 50.0±0.0 | 40.0±0.0 | 4.0±4.9 |
| 16 | Which fuel type showed the hig... | 10 | 100.0% | 87.0±12.7 | 50.0±0.0 | 36.0±12.0 | 1.0±3.0 |
| 17 | What is the growth rate among ... | 10 | 80.0% | 91.2±16.2 | 50.0±0.0 | 35.0±13.2 | 6.2±4.8 |
| 18 | Which country has the highest ... | 10 | 100.0% | 100.0±0.0 | 50.0±0.0 | 40.0±0.0 | 10.0±0.0 |
| 19 | Compare England vs Scotland ve... | 10 | 100.0% | 50.0±20.0 | 10.0±20.0 | 40.0±0.0 | 0.0±0.0 |
| 20 | Which districts register the m... | 10 | 100.0% | 81.0±27.0 | 45.0±15.0 | 36.0±12.0 | 0.0±0.0 |
| 21 | Find the top regions for BMW r... | 10 | 100.0% | 99.0±3.0 | 50.0±0.0 | 40.0±0.0 | 9.0±3.0 |
| 22 | Find the top regions for MERCE... | 10 | 100.0% | 100.0±0.0 | 50.0±0.0 | 40.0±0.0 | 10.0±0.0 |
| 23 | Find the top regions for AUDI ... | 10 | 100.0% | 91.0±3.0 | 50.0±0.0 | 40.0±0.0 | 1.0±3.0 |
| 24 | Find the top regions for PORSC... | 10 | 100.0% | 100.0±0.0 | 50.0±0.0 | 40.0±0.0 | 10.0±0.0 |

## Technical Details

- **Evaluator Version**: Unknown
- **Expected Results File**: tests/test_data/generated/complete_test_data.json
- **Database Path**: data/registered_vehicles.sqlite
- **Evaluation Start**: 2025-09-09T21:56:21.381762
- **Evaluation End**: 2025-09-09T22:26:25.074396

