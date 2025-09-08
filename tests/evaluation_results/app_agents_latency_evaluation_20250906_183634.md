# App Agent Latency Evaluation Report

**Generated on:** 2025-09-06 18:36:34  
**Evaluation Duration:** 15.26 seconds  
**Questions Evaluated:** 2  
**Successful Pipelines:** 2  
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
| **Count** | 2 |
| **Mean** | 6.627s |
| **Median** | 6.627s |
| **Std Dev** | 1.172s |
| **Min** | 5.456s |
| **Max** | 7.799s |
| **P25** | 6.042s |
| **P75** | 7.213s |
| **P95** | 7.682s |
| **P99** | 7.776s |



## Step-by-Step Performance Analysis

### Step 1: SQL Generation

| Metric | Value |
|--------|-------|
| **Count** | 2 |
| **Mean** | 3.236s |
| **Median** | 3.236s |
| **Std Dev** | 0.952s |
| **Min** | 2.284s |
| **Max** | 4.189s |
| **P25** | 2.760s |
| **P75** | 3.713s |
| **P95** | 4.094s |
| **P99** | 4.170s |


### Step 2: SQL Review

| Metric | Value |
|--------|-------|
| **Count** | 2 |
| **Mean** | 2.260s |
| **Median** | 2.260s |
| **Std Dev** | 0.040s |
| **Min** | 2.220s |
| **Max** | 2.300s |
| **P25** | 2.240s |
| **P75** | 2.280s |
| **P95** | 2.296s |
| **P99** | 2.299s |


### Step 3: Query Execution

| Metric | Value |
|--------|-------|
| **Count** | 2 |
| **Mean** | 0.128s |
| **Median** | 0.128s |
| **Std Dev** | 0.032s |
| **Min** | 0.096s |
| **Max** | 0.160s |
| **P25** | 0.112s |
| **P75** | 0.144s |
| **P95** | 0.157s |
| **P99** | 0.159s |


### Step 4: Visualization Generation

| Metric | Value |
|--------|-------|
| **Count** | 2 |
| **Mean** | 1.003s |
| **Median** | 1.003s |
| **Std Dev** | 0.148s |
| **Min** | 0.855s |
| **Max** | 1.151s |
| **P25** | 0.929s |
| **P75** | 1.077s |
| **P95** | 1.136s |
| **P99** | 1.148s |


## Performance Insights

### Key Findings

- **Slowest Step**: step_1_generate_sql (avg: 3.236s)
- **Fastest Step**: step_3_execute_query (avg: 0.128s)
- **Pipeline Efficiency**: 100.0% of time spent in measured steps
- **Success Rate**: 100.0% (2/2)

## Detailed Results

| Q# | Question | Total Duration | Step1 | Step2 | Step3 | Step4 | Status |
|----|----------|----------------|-------|-------|-------|-------|---------|
| 1 | What are the monthly registration trends for BMW, ... | 7.80s | 4.19s | 2.30s | 0.16s | 1.15s | ✅ Success |
| 2 | What are the monthly registrations for electric ve... | 5.46s | 2.28s | 2.22s | 0.10s | 0.86s | ✅ Success |

## Failure Analysis

✅ No pipeline failures detected!

