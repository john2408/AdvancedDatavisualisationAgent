# Dummy:
"What were the total monthly registrations for electric SUVs in the UK during 2023?"


### Testing the `INFORMATION_SEEKING` Workflow

This path is for questions requiring textual answers from internal documents or the web.

---
**Example 1: General Knowledge Query**

* **Prompt:** `"Tell me about the Aston Martin DBX model."`
* **Expected Action:** `INFORMATION_SEEKING`
* **Reasoning:** The prompt uses the keyword `"tell me about"` and asks for descriptive, non-numerical information about a specific model. This clearly aligns with the **Knowledge Keywords** and **Topical Questions** indicators.
* **Expected Agent Workflow:**
    1.  **Orchestrator** classifies the intent as `INFORMATION_SEEKING`.
    2.  It delegates to the **Information Retrieval Agent**.
    3.  The agent first searches the internal Elasticsearch knowledge base for documents about the "Aston Martin DBX".
    4.  If no internal documents are found, it automatically calls the **Web Crawling Agent** to get the information from the internet.
    5.  A final text-based summary is returned to the user.

---
**Example 2: Document-Specific Query**

* **Prompt:** `"What were the key findings from the 2023 annual report regarding SUV sales?"`
* **Expected Action:** `INFORMATION_SEEKING`
* **Reasoning:** This prompt explicitly mentions a specific internal document (`"annual report"`) and asks for qualitative findings, matching the **Document Keywords** indicator.
* **Expected Agent Workflow:**
    1.  **Orchestrator** classifies the intent as `INFORMATION_SEEKING`.
    2.  It delegates to the **Information Retrieval Agent**, which will specifically search for the "2023 annual report" and synthesize an answer about SUV sales from its content.

---
### Testing the `NEW_QUERY` (SQL) Workflow

This path is for questions that require fetching and calculating numerical data from your database.

---
**Example 3: Simple Data Request**

* **Prompt:** `"Show me the total number of electric vehicles registered in London in 2024."`
* **Expected Action:** `NEW_QUERY`
* **Reasoning:** This is a classic data request. It uses the keyword `"show me"` and asks for a specific number (`"total number"`) with clear filters (electric, London, 2024). This matches the **Data Request Keywords** and **Aggregation Requests** indicators.
* **Expected Agent Workflow:**
    1.  **Orchestrator** classifies the intent as `NEW_QUERY`.
    2.  **SQL Query Generator** creates the SQL query.
    3.  **SQL Query Reviewer** validates the query.
    4.  **Compliance Checker** ensures it's safe.
    5.  The **Code Engine function** (`sql-data-fetcher-tool`) executes the query.
    6.  **Data Analyst** and **Visualization Agents** create a chart (likely a simple number card or bar chart).
    7.  **Result Interpreter** provides a summary sentence.
    8.  **Orchestrator** generates follow-up questions.

---
**Example 4: Comparative Analysis**

* **Prompt:** `"Compare the year-over-year registration growth for BMW, Audi, and Mercedes in Germany."`
* **Expected Action:** `NEW_QUERY`
* **Reasoning:** The keyword `"compare"` combined with specific entities (BMW, Audi, Mercedes) and a time-based metric ("year-over-year growth") clearly indicates a request for a new analysis from the database.
* **Expected Agent Workflow:** The full SQL pipeline is executed, likely resulting in a multi-line chart or a grouped bar chart visualizing the growth percentages for the three OEMs.

---
### Testing the `FOLLOW_UP` Workflow

This path is for questions about the data and chart currently on the screen.

**Scenario Context:** Assume the previous query was "Show total registrations by OEM in 2024," and a bar chart is now displayed.

---
**Example 5: Data Clarification**

* **Prompt:** `"Which OEM had the lowest number of registrations?"`
* **Expected Action:** `FOLLOW_UP`
* **Reasoning:** The question is a **Comparative (within current data)** query. It directly references the data in the visible chart without asking for any new entities or timeframes.
* **Expected Agent Workflow:**
    1.  **Orchestrator** classifies the intent as `FOLLOW_UP`.
    2.  It delegates to the **Result Interpreter Agent** (using the `data_question_answering_task`).
    3.  This agent analyzes the existing data context (the DataFrame already in memory) to find the OEM with the minimum value and provides a direct text answer.
    4.  No new SQL query is run.

---
**Example 6: Visualization Change**

* **Prompt:** `"Can you show this as a pie chart instead?"`
* **Expected Action:** `FOLLOW_UP`
* **Reasoning:** This is a clear **Visualization Change** request. The user wants to see the *same data* presented in a different format.
* **Expected Agent Workflow:**
    1.  **Orchestrator** classifies as `FOLLOW_UP`.
    2.  It delegates to the **Visualization Agent** (using the `alternative_visualization_task`).
    3.  The agent takes the existing DataFrame and re-renders it as a pie chart.
    4.  No new SQL query is run.