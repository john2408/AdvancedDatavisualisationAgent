import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
from frontend.utils import load_multiple_css

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


# --- PLACEHOLDER BACKEND FUNCTIONS ---
# These functions simulate the real backend logic.
# Developers will replace these with the actual implementations.

def connect_to_supabase():
    """Placeholder for initializing the Supabase client."""
    # In a real app, this would use st.secrets to get credentials
    # and return a Supabase client object.
    return {"status": "connected"}

def query_supabase_db(sql_query: str):
    """Placeholder for running a SQL query against Supabase."""
    st.info(f"Executing SQL: `{sql_query}`")
    time.sleep(1.5)
    # Simulate a successful query returning data for a chart
    data = {
        'Product': ['Vehicle A', 'Vehicle B', 'Vehicle C', 'Vehicle D'],
        'Sales': [450, 520, 380, 610],
        'Region': ['North', 'South', 'North', 'East']
    }
    return pd.DataFrame(data)

def get_rag_context(query: str):
    """Placeholder for the RAG pipeline with IBM Elasticsearch."""
    if "competitor" in query.lower():
        time.sleep(1)
        return "Recent internal analysis shows that Competitor Z's new model launch has impacted sales of 'Vehicle C' in the North region."
    return None

def run_agent_crew(user_query: str):
    """
    Main placeholder for running the entire CrewAI process.
    This orchestrates the other placeholders.
    """
    # 1. Planner & Research Agent Simulation
    rag_context = get_rag_context(user_query)

    # 2. SQL Agent Simulation
    sql_query = "SELECT product, SUM(sales) as total_sales FROM sales_data GROUP BY product;"

    # 3. Data Analyst Agent Simulation
    df = query_supabase_db(sql_query)
    fig = px.bar(df, x='Product', y='Sales', title='Total Sales by Product', template="seaborn")
    fig.update_layout(title_x=0.5)
    plotly_spec = fig.to_json()

    # 4. Presentation Agent Simulation
    summary = "Here are the total sales figures for each product. Vehicle D shows the highest sales performance."
    
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
                beautiful visualizations for you.
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.write("") # Spacer
    cols = st.columns([1, 1, 1, 1.5]) # Adjust column ratios for centering
    with cols[0]:
        if st.button("“Show sales by product”"):
            st.session_state.run_query = "Show me the sales by product"
    with cols[1]:
        if st.button("“Monthly trends 2024”"):
            st.session_state.run_query = "What are the monthly trends for 2024?"
    with cols[2]:
        if st.button("“Top performing regions”"):
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
        "content": "Hello! I'm your Visualization Assistant.",
        "time": datetime.now().strftime("%I:%M:%S %p")
    }]
if "last_visualization" not in st.session_state:
    st.session_state.last_visualization = None
if "run_query" not in st.session_state:
    st.session_state.run_query = None

# --- SIDEBAR (CHAT INTERFACE) ---

with st.sidebar:
    st.title("📊 Visualization Agent")
    st.markdown("#### Chat with Your Supabase Data")
    st.markdown("<p style='color: #6B7280 !important;'>Real-time analytics from your star schema database</p>", unsafe_allow_html=True)
    st.divider()

    # Chat history display area
    chat_container = st.container(height=350)
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                st.caption(message["time"])

    # Chat input
    if prompt := st.chat_input("Ask about your Supabase data..."):
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
    with st.spinner("Agents are analyzing your request..."):
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