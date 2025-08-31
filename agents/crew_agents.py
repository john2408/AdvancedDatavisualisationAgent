from crewai import Agent, Task, Crew
from pydantic import BaseModel, Field
from typing import List
from agents.tools.visualization_tool import DataFrameVisualizationTool
import yaml
import os


# Define file paths for YAML configurations relative to this file
current_dir = os.path.dirname(os.path.abspath(__file__))
files = {
    'agents': os.path.join(current_dir, 'config', 'agents.yaml'),
    'tasks': os.path.join(current_dir, 'config', 'tasks.yaml'),
}

# Load configurations from YAML files
configs = {}
for config_type, file_path in files.items():
    with open(file_path, 'r') as file:
        configs[config_type] = yaml.safe_load(file)

# Assign loaded configurations to specific variables
agents_config = configs['agents']
tasks_config = configs['tasks']


class SQLQuery(BaseModel):
    sqlquery: str = Field(..., description="The raw sql query for the user input")

class ReviewedSQLQuery(BaseModel):
    reviewed_sqlquery: str = Field(..., description="The reviewed sql query for the raw sql query")

class ComplianceReport(BaseModel):
    report: str = Field(..., description="A markdown-formatted compliance report with a verdict and any flagged issues.")

class VisualizationJSON(BaseModel):
    plot_type: str = Field(..., description="Type of the plot")
    x_column: str = Field(..., description="X-axis column")
    y_column: str = Field(..., description="Y-axis column")
    color_column: str = Field(default="", description="Column for color grouping")
    title: str = Field(..., description="Title of the plot")
    aggregation: str = Field(default="sum", description="Aggregation method")
    transformation: str = Field(default="", description="Data transformation applied")
    plot_spec: str = Field(..., description="JSON specification for the plot")

class DataAnalysisReport(BaseModel):
    analysis: str = Field(..., description="Data analysis and insights from the query results")
    recommended_visualizations: List[str] = Field(..., description="List of recommended visualization types")
    key_findings: List[str] = Field(..., description="Key findings from the data")

class OrchestrationDecision(BaseModel):
    action_type: str = Field(..., description="Either 'new_query' or 'follow_up'")
    reasoning: str = Field(..., description="Explanation for the decision")
    confidence: float = Field(..., description="Confidence level between 0.0 and 1.0")

class DataQuestionAnswer(BaseModel):
    answer: str = Field(..., description="Comprehensive answer to the user's question about the data")
    referenced_data_points: List[str] = Field(..., description="Specific data points referenced in the answer")
    insights: List[str] = Field(..., description="Key insights derived from the data")

class FollowUpQuestions(BaseModel):
    questions: List[str] = Field(..., description="List of relevant follow-up questions")
    categories: List[str] = Field(..., description="Categories of the follow-up questions (e.g., 'trends', 'comparisons')")

class ChartTypeSelection(BaseModel):
    chart_type: str = Field(..., description="The most appropriate chart type for the data")

# Creating Agents
query_generator_agent = Agent(
  config=agents_config['query_generator_agent']
)

query_reviewer_agent = Agent(
  config=agents_config['query_reviewer_agent']
)

compliance_checker_agent = Agent(
  config=agents_config['compliance_checker_agent']
)

data_analyst_agent = Agent(
  config=agents_config['data_analyst_agent']
)

visualization_agent = Agent(
  config=agents_config['visualization_agent'],
  tools=[DataFrameVisualizationTool()]
)

orchestration_agent = Agent(
  config=agents_config['orchestration_agent']
)

chart_type_selection_agent = Agent(
  config=agents_config['chart_type_selection_agent']
)

# Creating Tasks
query_task = Task(
  config=tasks_config['query_task'],
  agent=query_generator_agent,
  output_pydantic=SQLQuery
)

review_task = Task(
  config=tasks_config['review_task'],
  agent=query_reviewer_agent,
  output_pydantic=ReviewedSQLQuery
)

compliance_task = Task(
  config=tasks_config['compliance_task'],
  agent=compliance_checker_agent,
  context=[review_task],
  output_pydantic=ComplianceReport
)

data_analysis_task = Task(
  config=tasks_config['data_analysis_task'],
  agent=data_analyst_agent,
  output_pydantic=DataAnalysisReport
)

visualization_task = Task(
  config=tasks_config['visualization_task'],
  agent=visualization_agent,
  output_pydantic=VisualizationJSON
)

orchestration_task = Task(
  config=tasks_config['orchestration_task'],
  agent=orchestration_agent,
  output_pydantic=OrchestrationDecision
)

data_question_answering_task = Task(
  config=tasks_config['data_question_answering_task'],
  agent=orchestration_agent,
  output_pydantic=DataQuestionAnswer
)

alternative_visualization_task = Task(
  config=tasks_config['alternative_visualization_task'],
  agent=visualization_agent,
  output_pydantic=VisualizationJSON
)

follow_up_questions_task = Task(
  config=tasks_config['follow_up_questions_task'],
  agent=orchestration_agent,
  output_pydantic=FollowUpQuestions
)

chart_type_selection_task = Task(
  config=tasks_config['chart_type_selection_agent_task'],
  agent=chart_type_selection_agent,
  output_pydantic=ChartTypeSelection
)


# Creating Crew objects for import
sql_generator_crew = Crew(
    agents=[query_generator_agent],
    tasks=[query_task],
    verbose=True
)

sql_reviewer_crew = Crew(
    agents=[query_reviewer_agent],
    tasks=[review_task],
    verbose=True
)

sql_compliance_crew = Crew(
    agents=[compliance_checker_agent],
    tasks=[compliance_task],
    verbose=True
)

data_analysis_crew = Crew(
    agents=[data_analyst_agent],
    tasks=[data_analysis_task],
    verbose=True
)

data_visualization_crew = Crew(
    agents=[visualization_agent],
    tasks=[visualization_task],
    verbose=True
)

orchestration_crew = Crew(
    agents=[orchestration_agent],
    tasks=[orchestration_task],
    verbose=True
)

data_question_crew = Crew(
    agents=[orchestration_agent],
    tasks=[data_question_answering_task],
    verbose=True
)

alternative_viz_crew = Crew(
    agents=[visualization_agent],
    tasks=[alternative_visualization_task],
    verbose=True
)

follow_up_crew = Crew(
    agents=[orchestration_agent],
    tasks=[follow_up_questions_task],
    verbose=True
)

chart_type_crew = Crew(
  agents=[chart_type_selection_agent],
  tasks=[chart_type_selection_task],
  verbose=True
)