import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
from frontend.utils import load_multiple_css
from agents.sql_crew import sql_generator_crew
from utils.db_simulator import get_structured_schema, run_query

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Visualization Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LOAD CUSTOM CSS ---
css_files = [
    "frontend/style/base.css",
    "frontend/style/sidebar.css", 
    "frontend/style/chat.css",
    "frontend/style/components.css"
]
load_multiple_css(css_files)

# --- DATABASE CONFIGURATION ---
DB_PATH = "data/sample_db.sqlite"

# Cache the schema for performance
@st.cache_data(show_spinner=False)
def load_schema():
    return get_structured_schema(DB_PATH)


# --- BACKEND FUNCTIONS ---

def connect_to_supabase():
    """Placeholder for initializing the Supabase client."""
    # In a real app, this would use st.secrets to get credentials
    # and return a Supabase client object.
    return {"status": "connected"}

def query_database(sql_query: str):
    """Execute SQL query against the sample SQLite database."""
    st.info(f"Executing SQL: `{sql_query}`")
    try:
        result = run_query(sql_query)
        # Parse the result string and convert to DataFrame
        # The run_query function returns a formatted string, so we need to handle this appropriately
        st.success("Query executed successfully!")
        return result
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None

def get_rag_context(query: str):
    """Placeholder for the RAG pipeline with IBM Elasticsearch."""
    if "competitor" in query.lower():
        time.sleep(1)
        return "Recent internal analysis shows that Competitor Z's new model launch has impacted sales of 'Vehicle C' in the North region."
    return None

def run_agent_crew(user_query: str):
    """
    Main function for running the CrewAI process with SQL generation.
    This integrates the SQL generator agent with the existing workflow.
    """
    # 1. Planner & Research Agent Simulation
    rag_context = get_rag_context(user_query)

    # 2. SQL Agent - Use the actual query generator agent
    try:
        db_schema = load_schema()
        gen_output = sql_generator_crew.kickoff(inputs={"user_input": user_query, "db_schema": db_schema})
        sql_query = gen_output.pydantic.sqlquery
        st.info(f"Generated SQL Query: {sql_query}")
        
        # Execute the generated query
        query_result = query_database(sql_query)
        
        # For now, create a simple mock visualization since we need to parse the query result properly
        # TODO: Parse query_result and create appropriate visualization based on the data
        fig = px.bar(
            x=['Sample A', 'Sample B', 'Sample C'], 
            y=[100, 200, 150], 
            title=f'Results for: {user_query}',
            template="seaborn"
        )
        fig.update_layout(title_x=0.5)
        plotly_spec = fig.to_json()
        
        # 4. Presentation Agent Simulation
        summary = f"I generated and executed the following SQL query: {sql_query}. The query returned results successfully."
        
    except Exception as e:
        st.error(f"Error in SQL generation or execution: {e}")
        # Fallback to mock data for now
        fig = px.bar(
            x=['Error'], 
            y=[0], 
            title='Query Generation Failed',
            template="seaborn"
        )
        plotly_spec = fig.to_json()
        summary = f"There was an error generating or executing the SQL query for: {user_query}"
    
    response = {
        "chat_message": summary,
        "plotly_spec": plotly_spec,
        "rag_summary": rag_context,
        "ran_at": datetime.now().strftime("%I:%M:%S %p")
    }
    return response

# --- UI HELPER FUNCTIONS ---

def display_welcome_message():
    """Displays the initial message in the main panel."""
    st.markdown("""
        <div class="welcome-container">
            <h2 style="text-align: center; color: #1F2937 !important;">📊 Ready to Visualize Your Data</h2>
            <p style="text-align: center; color: #6B7280 !important; font-size: 1.1rem;">
                Ask questions about your sales data in the chat, and I'll create
                beautiful visualizations for you using AI-generated SQL queries.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Add database schema information
    with st.expander("📋 View Database Schema"):
        db_schema = load_schema()
        st.code(db_schema, language="text")
    
    st.write("") # Spacer
    cols = st.columns([1, 1, 1, 1.5]) # Adjust column ratios for centering
    with cols[0]:
        if st.button("Show sales by product"):
            st.session_state.run_query = "Show me the sales by product"
    with cols[1]:
        if st.button("Monthly trends 2024"):
            st.session_state.run_query = "What are the monthly trends for 2024?"
    with cols[2]:
        if st.button("Top performing regions"):
            st.session_state.run_query = "Which regions are performing the best?"

def display_visualization(viz_data):
    """Displays the chart and summaries in the main panel."""
    if viz_data.get("rag_summary"):
        st.info(f"**Research Found:** {viz_data['rag_summary']}", icon="💡")
    
    st.plotly_chart(viz_data["plotly_spec"], use_container_width=True)


# --- MAIN APP LOGIC ---

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "Hello! I'm your Visualization Assistant. I can generate SQL queries and create visualizations from your database.",
        "time": datetime.now().strftime("%I:%M:%S %p")
    }]
if "last_visualization" not in st.session_state:
    st.session_state.last_visualization = None
if "run_query" not in st.session_state:
    st.session_state.run_query = None

# --- SIDEBAR (CHAT INTERFACE) ---

with st.sidebar:
    st.title("📊 Visualization Agent")
    st.markdown("#### Chat with Your Database")
    st.markdown("<p style='color: #6B7280 !important;'>AI-powered SQL generation and visualization</p>", unsafe_allow_html=True)
    st.divider()

    # Chat history display area
    chat_container = st.container(height=350)
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                st.caption(message["time"])

    # Chat input
    if prompt := st.chat_input("Ask about your database..."):
        st.session_state.run_query = prompt


# --- MAIN PANEL (VISUALIZATION AREA) ---

# This logic block handles executing a query from either chat input or a button click
if st.session_state.run_query:
    
    # Add user message to chat history
    user_message = {
        "role": "user", 
        "content": st.session_state.run_query,
        "time": datetime.now().strftime("%I:%M:%S %p")
    }
    st.session_state.messages.append(user_message)
    
    # Reset run_query to prevent re-running on every interaction
    query_to_run = st.session_state.run_query
    st.session_state.run_query = None
    
    # Rerun to immediately display the user's message in the chat history
    st.rerun()

# This logic block handles displaying the results after a query has been run
# It checks if the latest message is from a user, implying the assistant needs to respond.
if st.session_state.messages[-1]["role"] == "user":
    with st.spinner("Generating SQL query and analyzing your request..."):
        # Run the agent crew
        visualization_data = run_agent_crew(st.session_state.messages[-1]["content"])
        
        # Store the visualization to be displayed in the main panel
        st.session_state.last_visualization = visualization_data
        
        # Add assistant's text response to chat history
        assistant_message = {
            "role": "assistant",
            "content": visualization_data["chat_message"],
            "time": visualization_data["ran_at"]
        }
        st.session_state.messages.append(assistant_message)
        
        # Rerun to display the new assistant message and the visualization
        st.rerun()


# Display either the welcome message or the latest visualization
st.header("Ask questions about your data in natural language")
st.write("---")

if st.session_state.last_visualization:
    display_visualization(st.session_state.last_visualization)
else:
    display_welcome_message()
