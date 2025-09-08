# App Agent Latency Evaluation Report

**Generated on:** 2025-09-06 18:42:53  
**Evaluation Duration:** 162.58 seconds  
**Questions Evaluated:** 24  
**Successful Pipelines:** 24  
**Failed Pipelines:** 0  

## Executive Summary

This report evaluates the latency performance of the 4-step agent pipeline:

1. **Step 1**: SQL Generation using CrewAI
2. **Step 2**: SQL Review using CrewAI
3. **Step 3**: Query Execution 
4. **Step 4**: Visualization Generation

## Overall Pipeline Performance

### Total Pipeline Duration (End-to-End)
| Metric | Value |
|--------|-------|
| **Count** | 24 |
| **Mean** | 5.769s |
| **Median** | 5.586s |
| **Std Dev** | 1.150s |
| **Min** | 3.811s |
| **Max** | 8.736s |
| **P25** | 4.914s |
| **P75** | 6.181s |
| **P95** | 8.307s |
| **P99** | 8.682s |



## Step-by-Step Performance Analysis

### Step 1: SQL Generation

| Metric | Value |
|--------|-------|
| **Count** | 24 |
| **Mean** | 2.068s |
| **Median** | 1.888s |
| **Std Dev** | 0.629s |
| **Min** | 1.323s |
| **Max** | 3.942s |
| **P25** | 1.702s |
| **P75** | 2.375s |
| **P95** | 3.360s |
| **P99** | 3.833s |


### Step 2: SQL Review

| Metric | Value |
|--------|-------|
| **Count** | 24 |
| **Mean** | 2.729s |
| **Median** | 2.675s |
| **Std Dev** | 0.639s |
| **Min** | 1.537s |
| **Max** | 4.878s |
| **P25** | 2.330s |
| **P75** | 2.985s |
| **P95** | 3.449s |
| **P99** | 4.554s |


### Step 3: Query Execution

| Metric | Value |
|--------|-------|
| **Count** | 24 |
| **Mean** | 0.171s |
| **Median** | 0.146s |
| **Std Dev** | 0.112s |
| **Min** | 0.034s |
| **Max** | 0.567s |
| **P25** | 0.096s |
| **P75** | 0.238s |
| **P95** | 0.312s |
| **P99** | 0.509s |


### Step 4: Visualization Generation

| Metric | Value |
|--------|-------|
| **Count** | 24 |
| **Mean** | 0.802s |
| **Median** | 0.770s |
| **Std Dev** | 0.132s |
| **Min** | 0.581s |
| **Max** | 1.174s |
| **P25** | 0.708s |
| **P75** | 0.856s |
| **P95** | 1.025s |
| **P99** | 1.141s |


## Performance Insights

### Key Findings

- **Slowest Step**: step_2_review_sql (avg: 2.729s)
- **Fastest Step**: step_3_execute_query (avg: 0.171s)
- **Pipeline Efficiency**: 100.0% of time spent in measured steps
- **Success Rate**: 100.0% (24/24)

## Detailed Results

| Q# | Question | Total Duration | Step1 | Step2 | Step3 | Step4 | Status |
|----|----------|----------------|-------|-------|-------|-------|---------|
| 1 | What are the monthly registration trends for BMW, ... | 8.74s | 3.94s | 3.47s | 0.15s | 1.17s | ✅ Success |
| 2 | What are the monthly registrations for electric ve... | 4.56s | 1.66s | 2.05s | 0.09s | 0.75s | ✅ Success |
| 3 | Provide a comparison of monthly registrations for ... | 6.17s | 1.74s | 3.27s | 0.16s | 0.99s | ✅ Success |
| 4 | Provide a comparison of monthly registrations for ... | 5.63s | 1.73s | 2.81s | 0.24s | 0.85s | ✅ Success |
| 5 | Monthly registrations for ELECTRIC and PATROL vehi... | 6.59s | 2.06s | 3.33s | 0.29s | 0.92s | ✅ Success |
| 6 | What are the top 5 car brands by total registratio... | 5.54s | 1.53s | 2.98s | 0.15s | 0.88s | ✅ Success |
| 7 | What are the monthly registrations in total since ... | 3.81s | 1.32s | 1.54s | 0.13s | 0.82s | ✅ Success |
| 8 | What are the year-over-year growth trends for elec... | 4.82s | 1.53s | 2.35s | 0.09s | 0.85s | ✅ Success |
| 9 | Year-over-year comparison of SUV registrations fro... | 4.85s | 1.74s | 2.25s | 0.15s | 0.71s | ✅ Success |
| 10 | Q1 2024 vs Q1 2023 comparison of total vehicle reg... | 5.31s | 1.72s | 2.83s | 0.07s | 0.70s | ✅ Success |

_... and 14 more results_

## Failure Analysis

✅ No pipeline failures detected!

