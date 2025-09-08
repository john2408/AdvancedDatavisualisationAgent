# App Agent Latency Evaluation Report

**Generated on:** 2025-09-06 18:58:01  
**Evaluation Duration:** 60.00 seconds  
**Questions Evaluated:** 1  
**Successful Pipelines:** 1  
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
| **Count** | 1 |
| **Mean** | 7.684s |
| **Median** | 7.684s |
| **Std Dev** | 0.000s |
| **Min** | 7.684s |
| **Max** | 7.684s |
| **P25** | 7.684s |
| **P75** | 7.684s |
| **P95** | 7.684s |
| **P99** | 7.684s |



## Step-by-Step Performance Analysis

### Step 1: SQL Generation

| Metric | Value |
|--------|-------|
| **Count** | 1 |
| **Mean** | 4.020s |
| **Median** | 4.020s |
| **Std Dev** | 0.000s |
| **Min** | 4.020s |
| **Max** | 4.020s |
| **P25** | 4.020s |
| **P75** | 4.020s |
| **P95** | 4.020s |
| **P99** | 4.020s |


### Step 2: SQL Review

| Metric | Value |
|--------|-------|
| **Count** | 1 |
| **Mean** | 2.535s |
| **Median** | 2.535s |
| **Std Dev** | 0.000s |
| **Min** | 2.535s |
| **Max** | 2.535s |
| **P25** | 2.535s |
| **P75** | 2.535s |
| **P95** | 2.535s |
| **P99** | 2.535s |


### Step 3: Query Execution

| Metric | Value |
|--------|-------|
| **Count** | 1 |
| **Mean** | 0.146s |
| **Median** | 0.146s |
| **Std Dev** | 0.000s |
| **Min** | 0.146s |
| **Max** | 0.146s |
| **P25** | 0.146s |
| **P75** | 0.146s |
| **P95** | 0.146s |
| **P99** | 0.146s |


### Step 4: Visualization Generation

| Metric | Value |
|--------|-------|
| **Count** | 1 |
| **Mean** | 0.982s |
| **Median** | 0.982s |
| **Std Dev** | 0.000s |
| **Min** | 0.982s |
| **Max** | 0.982s |
| **P25** | 0.982s |
| **P75** | 0.982s |
| **P95** | 0.982s |
| **P99** | 0.982s |


## Performance Insights

### Key Findings

- **Slowest Step**: step_1_generate_sql (avg: 4.020s)
- **Fastest Step**: step_3_execute_query (avg: 0.146s)
- **Pipeline Efficiency**: 100.0% of time spent in measured steps
- **Success Rate**: 100.0% (1/1)

## Detailed Results

| Q# | Question | Total Duration | Step1 | Step2 | Step3 | Step4 | Status |
|----|----------|----------------|-------|-------|-------|-------|---------|
| 1 | What are the top 5 car brands by total registratio... | 7.68s | 4.02s | 2.54s | 0.15s | 0.98s | ✅ Success |

## Failure Analysis

✅ No pipeline failures detected!

