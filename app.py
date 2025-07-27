import streamlit as st
import pandas as pd
import time
import json
from datetime import datetime
from frontend.utils import load_multiple_css
from agents.crew_agents import (
    sql_generator_crew, 
    sql_reviewer_crew, 
    data_visualization_crew,
    orchestration_crew,
    data_question_crew,
    alternative_viz_crew,
    follow_up_crew
)
from backend.sql_utils import get_structured_schema, run_query
import plotly.express as px
import plotly.graph_objects as go
from omegaconf import OmegaConf

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

# --- LOAD CONFIGURATION ---
config = OmegaConf.load("config.yaml")
DB_PATH = config.db_path
db_schema_user = config.db_schema_user
db_schema_agent = config.db_schema_agent

# Cache the schema for performance
@st.cache_data(show_spinner=False)
def load_schema_user():
    return db_schema_user


# --- BACKEND FUNCTIONS ---
def query_database(sql_query: str):
    """Execute SQL query against the SQLite database and return DataFrame."""
    st.info(f"Executing SQL: `{sql_query}`")
    try:
        result_df = run_query(sql_query, DB_PATH)
        
        # Check if we got an error DataFrame
        if "Error" in result_df.columns:
            st.error(f"Error executing query: {result_df['Error'].iloc[0]}")
            return None
        
        st.success("Query executed successfully!")
        
        # Display the raw result for debugging
        with st.expander("🔍 Debug: Raw Query Result"):
            st.text("Raw DataFrame info:")
            st.text(f"Shape: {result_df.shape}")
            st.text(f"Columns: {list(result_df.columns)}")
            st.dataframe(result_df)
        
        return result_df
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None

def get_rag_context(query: str):
    """Placeholder for the RAG pipeline with IBM Elasticsearch."""
    if "competitor" in query.lower():
        time.sleep(1)
        return "Recent internal analysis shows that Competitor Z's new model launch has impacted sales of 'Vehicle C' in the North region."
    return None

def create_plotly_from_json(plot_spec_json: str, df: pd.DataFrame) -> go.Figure:
    """Create a Plotly figure from JSON specification and DataFrame."""
    try:
        plot_spec = json.loads(plot_spec_json)
        
        if "error" in plot_spec:
            st.error(f"Plot specification error: {plot_spec['error']}")
            return None
        
        plot_type = plot_spec.get("type")
        data = plot_spec.get("data", {})
        layout = plot_spec.get("layout", {})
        
        if not data:
            st.warning("No data found in plot specification")
            return None
        
        fig = None
        
        if plot_type == "bar":
            if "color" in data and data["color"]:
                # Grouped bar chart
                df_plot = pd.DataFrame({
                    "x": data["x"],
                    "y": data["y"],
                    "color": data["color"]
                })
                fig = px.bar(df_plot, x="x", y="y", color="color", title=layout.get("title"))
            else:
                # Simple bar chart
                fig = px.bar(x=data.get("x", []), y=data.get("y", []), title=layout.get("title"))
                
        elif plot_type == "line":
            if "color" in data and data["color"]:
                df_plot = pd.DataFrame({
                    "x": data["x"],
                    "y": data["y"],
                    "color": data["color"]
                })
                fig = px.line(df_plot, x="x", y="y", color="color", title=layout.get("title"))
            else:
                fig = px.line(x=data.get("x", []), y=data.get("y", []), title=layout.get("title"))
                
        elif plot_type == "scatter":
            if "color" in data and data["color"]:
                df_plot = pd.DataFrame({
                    "x": data["x"],
                    "y": data["y"],
                    "color": data["color"]
                })
                fig = px.scatter(df_plot, x="x", y="y", color="color", title=layout.get("title"))
            else:
                fig = px.scatter(x=data.get("x", []), y=data.get("y", []), title=layout.get("title"))
                
        elif plot_type == "pie":
            if "values" in data and "labels" in data:
                fig = px.pie(values=data["values"], names=data["labels"], title=layout.get("title"))
            
        elif plot_type == "histogram":
            if "x" in data:
                fig = px.histogram(x=data["x"], title=layout.get("title"))
            
        elif plot_type == "box":
            if "y" in data:
                fig = px.box(y=data["y"], title=layout.get("title"))
            elif "x" in data:
                fig = px.box(y=data["x"], title=layout.get("title"))
                
        elif plot_type == "heatmap":
            if "z" in data and "x" in data and "y" in data:
                fig = px.imshow(
                    z=data["z"], 
                    x=data["x"], 
                    y=data["y"], 
                    title=layout.get("title"),
                    text_auto=True
                )
        
        if fig:
            # Apply any additional layout configurations
            if layout.get("xaxis", {}).get("title"):
                fig.update_xaxes(title_text=layout["xaxis"]["title"])
            if layout.get("yaxis", {}).get("title"):
                fig.update_yaxes(title_text=layout["yaxis"]["title"])
                
            # Set responsive layout
            fig.update_layout(
                height=500,
                showlegend=layout.get("showlegend", True)
            )
                
        return fig
        
    except json.JSONDecodeError as e:
        st.error(f"Error parsing plot JSON: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating plot from JSON: {e}")
        return None

# --- STEP FUNCTIONS ---

# --- ORCHESTRATION FUNCTIONS ---

def orchestrate_user_intent(user_query: str, conversation_history: list, current_data_context: dict) -> dict:
    """Determine if this is a new query or follow-up question."""
    try:
        st.info("🤔 Understanding your intent...")
        
        # Format conversation history for the agent
        history_text = ""
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            history_text += f"{msg['role']}: {msg['content']}\n"
        
        # Format current data context
        data_context_text = ""
        if current_data_context:
            data_context_text = f"Current data available: {current_data_context.get('summary', 'No data context')}"
        
        orchestration_output = orchestration_crew.kickoff(inputs={
            "user_query": user_query,
            "conversation_history": history_text,
            "current_data_context": data_context_text
        })
        
        decision = orchestration_output.pydantic
        
        st.success(f"🎯 Intent: {decision.action_type.upper()} (Confidence: {decision.confidence:.1%})")
        
        return {
            "success": True,
            "action_type": decision.action_type,
            "reasoning": decision.reasoning,
            "confidence": decision.confidence
        }
        
    except Exception as e:
        st.warning(f"⚠️ Intent detection failed, defaulting to new query: {e}")
        return {
            "success": False,
            "action_type": "new_query",
            "reasoning": "Fallback to new query due to error",
            "confidence": 0.5
        }

def answer_data_question(user_question: str, current_data: pd.DataFrame, data_summary: str, chart_info: dict) -> dict:
    """Answer questions about current data visualization."""
    try:
        st.info("🔍 Analyzing current data to answer your question...")
        
        # Prepare data context
        data_dict = current_data.to_dict('records') if current_data is not None else []
        data_stats = {
            "rows": len(current_data),
            "columns": list(current_data.columns),
            "sample": current_data.head(3).to_dict('records') if current_data is not None else []
        }
        
        chart_context = {
            "type": chart_info.get("plot_type", "unknown"),
            "title": chart_info.get("title", ""),
            "columns_used": {
                "x": chart_info.get("x_column", ""),
                "y": chart_info.get("y_column", ""),
                "color": chart_info.get("color_column", "")
            }
        }
        
        answer_output = data_question_crew.kickoff(inputs={
            "user_question": user_question,
            "current_data": str(data_stats),
            "data_summary": data_summary,
            "chart_info": str(chart_context)
        })
        
        answer = answer_output.pydantic
        
        st.success("✅ Found insights in your data!")
        
        return {
            "success": True,
            "answer": answer.answer,
            "referenced_data_points": answer.referenced_data_points,
            "insights": answer.insights
        }
        
    except Exception as e:
        st.error(f"❌ Error answering data question: {e}")
        return {
            "success": False,
            "answer": "I'm having trouble analyzing the current data. Please try rephrasing your question.",
            "referenced_data_points": [],
            "insights": []
        }

def generate_alternative_visualization(user_request: str, current_data: pd.DataFrame, current_chart_type: str) -> dict:
    """Generate alternative visualization for current data."""
    try:
        st.info("🎨 Creating alternative visualization...")
        
        # Prepare data for visualization
        dataframe_json = current_data.to_json(orient='records')
        
        alt_viz_output = alternative_viz_crew.kickoff(inputs={
            "user_request": user_request,
            "current_data": dataframe_json,
            "current_chart_type": current_chart_type
        })
        
        viz_spec = alt_viz_output.pydantic
        
        # Create Plotly figure from specification
        if viz_spec.plot_spec:
            figure = create_plotly_from_json(viz_spec.plot_spec, current_data)
            if figure:
                st.success("✨ Alternative visualization created!")
                return {
                    "success": True,
                    "figure": figure,
                    "plot_type": viz_spec.plot_type,
                    "title": viz_spec.title,
                    "summary": f"Created {viz_spec.plot_type} chart: {viz_spec.title}"
                }
        
        return {
            "success": False,
            "figure": None,
            "summary": "Could not create alternative visualization"
        }
        
    except Exception as e:
        st.error(f"❌ Error creating alternative visualization: {e}")
        return {
            "success": False,
            "figure": None,
            "summary": f"Visualization generation failed: {str(e)}"
        }

def generate_follow_up_questions(data_analysis: str, original_query: str, data_insights: list, db_schema: str) -> dict:
    """Generate relevant follow-up questions based on available data schema."""
    try:
        st.info("💡 Generating follow-up questions...")
        
        follow_up_output = follow_up_crew.kickoff(inputs={
            "data_analysis": data_analysis,
            "original_query": original_query,
            "data_insights": ", ".join(data_insights) if data_insights else "No specific insights available",
            "db_schema": db_schema
        })
        
        follow_up = follow_up_output.pydantic
        
        st.success(f"📋 Generated {len(follow_up.questions)} follow-up questions!")
        
        return {
            "success": True,
            "questions": follow_up.questions,
            "categories": follow_up.categories
        }
        
    except Exception as e:
        st.warning(f"⚠️ Could not generate follow-up questions: {e}")
        return {
            "success": False,
            "questions": [],
            "categories": []
        }

# --- STEP FUNCTIONS ---

def step_1_generate_sql(user_query: str) -> dict:
    """Step 1: Generate initial SQL query using the generator agent."""
    try:
        db_schema = db_schema_agent
        st.info("🤖 Generating initial SQL query...")
        
        gen_output = sql_generator_crew.kickoff(inputs={
            "user_input": user_query, 
            "db_schema": db_schema
        })
        initial_sql = gen_output.pydantic.sqlquery
        
        st.success(f"📝 Initial SQL Query Generated!")
        st.code(initial_sql, language="sql")
        
        return {
            "success": True,
            "initial_sql": initial_sql,
            "error": None
        }
    except Exception as e:
        st.error(f"❌ Error generating SQL: {e}")
        return {
            "success": False,
            "initial_sql": None,
            "error": str(e)
        }

def step_2_review_sql(initial_sql: str) -> dict:
    """Step 2: Review and optimize the SQL using GPT-4o reviewer."""
    try:
        db_schema = db_schema_agent
        st.info("🔍 Reviewing SQL with GPT-4o verifier...")
        
        review_output = sql_reviewer_crew.kickoff(inputs={
            "sql_query": initial_sql, 
            "db_schema": db_schema
        })
        reviewed_sql = review_output.pydantic.reviewed_sqlquery
        
        # Show comparison if the SQL was changed
        if initial_sql.strip() != reviewed_sql.strip():
            st.success("✨ SQL query was optimized by the reviewer!")
            with st.expander("🔄 SQL Query Comparison"):
                col1, col2 = st.columns(2)
                with col1:
                    st.text("Original SQL:")
                    st.code(initial_sql, language="sql")
                with col2:
                    st.text("Reviewed SQL:")
                    st.code(reviewed_sql, language="sql")
        else:
            st.success("✅ SQL query approved by reviewer (no changes needed)")
        
        st.info(f"🎯 Final SQL Query: {reviewed_sql}")
        
        return {
            "success": True,
            "reviewed_sql": reviewed_sql,
            "was_changed": initial_sql.strip() != reviewed_sql.strip(),
            "error": None
        }
    except Exception as e:
        st.error(f"❌ Error reviewing SQL: {e}")
        return {
            "success": False,
            "reviewed_sql": initial_sql,  # Fallback to original
            "was_changed": False,
            "error": str(e)
        }

def step_3_execute_query(reviewed_sql: str) -> dict:
    """Step 3: Execute the reviewed query and return results."""
    try:
        st.info("🔄 Executing SQL query...")
        query_result = query_database(reviewed_sql)
        
        if query_result is not None and isinstance(query_result, pd.DataFrame) and not query_result.empty:
            if "Error" not in query_result.columns:
                st.success(f"✅ Query executed successfully! Retrieved {len(query_result)} rows.")
                return {
                    "success": True,
                    "query_result": query_result,
                    "error": None
                }
            else:
                error_msg = query_result["Error"].iloc[0]
                st.error(f"❌ Query execution error: {error_msg}")
                return {
                    "success": False,
                    "query_result": None,
                    "error": error_msg
                }
        else:
            st.warning("⚠️ Query executed but returned no data")
            return {
                "success": False,
                "query_result": None,
                "error": "No data returned"
            }
    except Exception as e:
        st.error(f"❌ Error executing query: {e}")
        return {
            "success": False,
            "query_result": None,
            "error": str(e)
        }

def step_4_generate_visualization(query_result: pd.DataFrame, user_query: str) -> dict:
    """Step 4: Generate visualization if we have valid results."""
    try:
        st.info("🎨 Generating visualization...")
        
        # Prepare data for visualization crew
        dataframe_json = query_result.to_json(orient='records')
        columns_info = list(query_result.columns)
        dtypes_info = query_result.dtypes.to_dict()
        sample_data = query_result.head(3).to_dict('records')
        
        # Convert dtypes to string representation
        dtypes_str = {col: str(dtype) for col, dtype in dtypes_info.items()}
        
        viz_inputs = {
            "dataframe_json": dataframe_json,
            "columns": ", ".join(columns_info),
            "shape": f"{query_result.shape[0]} rows × {query_result.shape[1]} columns",
            "dtypes": str(dtypes_str),
            "sample_data": str(sample_data),
            "user_question": user_query,
            "analysis": f"Data analysis for: {user_query}. The query returned {len(query_result)} rows with columns: {', '.join(columns_info)}."
        }
        
        try:
            # Run the visualization crew
            viz_output = data_visualization_crew.kickoff(inputs=viz_inputs)
            
            # Extract the plot specification
            if hasattr(viz_output, 'pydantic') and hasattr(viz_output.pydantic, 'plot_spec'):
                plot_spec = viz_output.pydantic.plot_spec
                viz_summary = f"Created {viz_output.pydantic.plot_type} chart: {viz_output.pydantic.title}"
                
                # Create the actual Plotly figure
                fig = create_plotly_from_json(plot_spec, query_result)
                
                if fig:
                    st.success("✨ Visualization created successfully!")
                    return {
                        "success": True,
                        "figure": fig,
                        "summary": viz_summary,
                        "error": None
                    }
                else:
                    st.warning("Failed to create visualization from plot specification")
                    return step_4_fallback_visualization(query_result)
            else:
                st.warning("Visualization crew completed but returned unexpected format")
                return step_4_fallback_visualization(query_result)
                
        except Exception as viz_error:
            st.warning(f"Could not generate visualization: {viz_error}")
            return step_4_fallback_visualization(query_result)
            
    except Exception as e:
        st.error(f"❌ Error in visualization process: {e}")
        return {
            "success": False,
            "figure": None,
            "summary": f"Visualization generation failed: {str(e)}",
            "error": str(e)
        }

def step_4_fallback_visualization(query_result: pd.DataFrame) -> dict:
    """Create a simple fallback visualization based on the data."""
    try:
        if len(query_result.columns) >= 2:
            # Try to create a simple bar chart with the first two columns
            first_col = query_result.columns[0]
            second_col = query_result.columns[1]
            
            # Check if we have appropriate data types
            if (query_result[first_col].dtype == 'object' or 
                str(query_result[first_col].dtype).startswith('string')) and \
               (query_result[second_col].dtype in ['int64', 'float64'] or 
                str(query_result[second_col].dtype).startswith('int') or 
                str(query_result[second_col].dtype).startswith('float')):
                
                fig = px.bar(query_result.head(10), x=first_col, y=second_col, 
                           title=f"{second_col} by {first_col}")
                viz_summary = f"Created fallback bar chart: {second_col} by {first_col}"
                st.info("✨ Created fallback visualization!")
                
                return {
                    "success": True,
                    "figure": fig,
                    "summary": viz_summary,
                    "error": None
                }
        
        st.info("💡 No suitable visualization could be created for this data type.")
        return {
            "success": False,
            "figure": None,
            "summary": "No visualization created - data available in table format",
            "error": "No suitable visualization for data type"
        }
        
    except Exception as fallback_error:
        st.warning(f"Fallback visualization also failed: {fallback_error}")
        return {
            "success": False,
            "figure": None,
            "summary": "Visualization generation failed completely",
            "error": str(fallback_error)
        }

def analyst_agents_flow(user_query: str):
    """
    Orchestrated function that intelligently routes between new queries and follow-up questions.
    Provides comprehensive assistance with data analysis and conversation memory.
    """
    # Get conversation context
    conversation_history = st.session_state.messages
    current_data_context = st.session_state.current_data_context
    
    # Step 0: Orchestrate user intent
    orchestration_result = orchestrate_user_intent(user_query, conversation_history, current_data_context)
    action_type = orchestration_result["action_type"]
    
    # Initialize response object
    response = {
        "chat_message": "",
        "plotly_figure": None,
        "query_result": None,
        "reviewed_sql": None,
        "rag_summary": None,
        "follow_up_questions": [],
        "action_type": action_type,
        "ran_at": datetime.now().strftime("%I:%M:%S %p")
    }
    
    if action_type == "follow_up" and current_data_context:
        # Handle follow-up questions about existing data
        st.info("🔄 This seems to be a follow-up question about your current data...")
        
        # Check if user wants alternative visualization
        if any(keyword in user_query.lower() for keyword in ["different chart", "another chart", "alternative", "different visualization", "bar chart", "line chart", "pie chart"]):
            alt_viz_result = generate_alternative_visualization(
                user_query, 
                current_data_context["query_result"], 
                current_data_context.get("chart_type", "unknown")
            )
            response["plotly_figure"] = alt_viz_result["figure"]
            response["chat_message"] = f"I created an alternative visualization for your data. {alt_viz_result['summary']}"
        else:
            # Answer question about current data
            answer_result = answer_data_question(
                user_query,
                current_data_context["query_result"],
                current_data_context.get("summary", ""),
                current_data_context.get("chart_info", {})
            )
            response["chat_message"] = answer_result["answer"]
            
            # Use existing visualization and data
            response["plotly_figure"] = current_data_context.get("plotly_figure")
            response["query_result"] = current_data_context.get("query_result")
            response["reviewed_sql"] = current_data_context.get("reviewed_sql")
        
        # Generate follow-up questions
        follow_up_result = generate_follow_up_questions(
            current_data_context.get("summary", ""),
            user_query,
            current_data_context.get("insights", []),
            db_schema_agent
        )
        response["follow_up_questions"] = follow_up_result["questions"]
        
    else:
        # Handle new data query - run full pipeline
        st.info("🚀 This looks like a new data request. Running full analysis pipeline...")
        st.session_state.conversation_mode = "new"
        
        # Planner & Research Agent Simulation
        rag_context = get_rag_context(user_query)
        response["rag_summary"] = rag_context
        
        # Step 1: Generate SQL
        sql_gen_result = step_1_generate_sql(user_query)
        if not sql_gen_result["success"]:
            response["chat_message"] = f"Failed to generate SQL query: {sql_gen_result['error']}"
            return response
        
        # Step 2: Review SQL
        sql_review_result = step_2_review_sql(sql_gen_result["initial_sql"])
        if not sql_review_result["success"]:
            response["chat_message"] = f"Failed to review SQL query: {sql_review_result['error']}"
            return response
        
        response["reviewed_sql"] = sql_review_result["reviewed_sql"]
        
        # Step 3: Execute Query
        query_exec_result = step_3_execute_query(sql_review_result["reviewed_sql"])
        if not query_exec_result["success"]:
            response["chat_message"] = f"Query execution failed: {query_exec_result['error']}"
            return response
        
        response["query_result"] = query_exec_result["query_result"]
        
        # Step 4: Generate Visualization
        viz_result = step_4_generate_visualization(query_exec_result["query_result"], user_query)
        response["plotly_figure"] = viz_result["figure"]
        
        # Update current data context for future follow-ups
        st.session_state.current_data_context = {
            "query_result": query_exec_result["query_result"],
            "plotly_figure": viz_result["figure"],
            "reviewed_sql": sql_review_result["reviewed_sql"],
            "original_query": user_query,
            "summary": viz_result.get("summary", ""),
            "chart_info": {
                "plot_type": viz_result.get("plot_type", "unknown"),
                "title": viz_result.get("title", ""),
            },
            "insights": viz_result.get("insights", []),
            "created_at": datetime.now().isoformat()
        }
        
        # Generate follow-up questions for new data
        follow_up_result = generate_follow_up_questions(
            viz_result.get("summary", ""),
            user_query,
            viz_result.get("insights", []),
            db_schema_agent
        )
        response["follow_up_questions"] = follow_up_result["questions"]
        
        # Create final summary message
        if viz_result["success"]:
            response["chat_message"] = f"I successfully generated and reviewed the SQL query, executed it, and created a visualization. {viz_result['summary']}"
        else:
            response["chat_message"] = f"I generated and executed the SQL query successfully. {viz_result['summary']} Check the results in the table below."
    
    # Store follow-up questions in session state
    st.session_state.follow_up_questions = response["follow_up_questions"]
    
    return response

# --- UI HELPER FUNCTIONS ---

def display_welcome_message():
    """Displays the initial message in the main panel."""
    st.markdown("""
        <div class="welcome-container">
            <h2 style="text-align: center; color: #1F2937 !important;">📊 Ready to Visualize Your Data</h2>
            <p style="text-align: center; color: #6B7280 !important; font-size: 1.1rem;">
                Ask questions about your vehicle registration data in the chat, and I'll create
                beautiful visualizations for you using AI-generated SQL queries.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Add database schema information
    with st.expander("📋 View Database Schema"):
        db_schema = load_schema_user()
        # Custom HTML/CSS for white background and black text
        st.markdown(db_schema
        )
    
    st.write("") # Spacer
    cols = st.columns([1, 1, 1, 1.5]) # Adjust column ratios for centering
    with cols[0]:
        if st.button("Which car manufacturers registered the most vehicles?"):
            st.session_state.run_query = "Which car manufacturers registered the most vehicles?"
    with cols[1]:
        if st.button("How many electric vehicles were registered?"):
            st.session_state.run_query = "How many electric vehicles were registered?"
    with cols[2]:
        if st.button("Which months had the highest vehicle registrations?"):
            st.session_state.run_query = "Which months had the highest vehicle registrations?"

def display_visualization(viz_data):
    """Displays the chart and summaries in the main panel."""
    if viz_data.get("rag_summary"):
        st.info(f"**Research Found:** {viz_data['rag_summary']}", icon="💡")
    
    # Display the final reviewed SQL query prominently
    if viz_data.get("reviewed_sql"):
        st.subheader("🎯 Final SQL Query (Reviewed by GPT-4o)")
        st.code(viz_data['reviewed_sql'], language="sql")
    
    # Display query result as nicely formatted table
    if viz_data.get("query_result") is not None:
        query_result = viz_data["query_result"]
        
        # Check if we have a valid DataFrame
        if isinstance(query_result, pd.DataFrame) and not query_result.empty:
            # Check if it's an error DataFrame
            if "Error" in query_result.columns:
                st.error("❌ Query Error")
                st.error(query_result["Error"].iloc[0])
            else:
                # Display successful results
                st.subheader("📊 Query Results")
                
                # Show summary statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows", len(query_result))
                with col2:
                    st.metric("Columns", len(query_result.columns))
                with col3:
                    if len(query_result.select_dtypes(include=['number']).columns) > 0:
                        # If there are numeric columns, show a sum of the first numeric column
                        numeric_col = query_result.select_dtypes(include=['number']).columns[0]
                        total_value = query_result[numeric_col].sum()
                        st.metric(f"Total {numeric_col}", f"{total_value:,.0f}")
                
                # Display the formatted table
                st.dataframe(
                    query_result,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Optional: Add download button for the data
                csv_data = query_result.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                # Add spacing before visualization
                st.write("")
                st.write("---")
        else:
            st.warning("No data returned from query")
    
    # Display plotly figure if available - THIS COMES AFTER THE TABLE
    if viz_data.get("plotly_figure"):
        st.subheader("📈 Data Visualization")
        
        # Display the figure
        try:
            st.plotly_chart(viz_data["plotly_figure"], use_container_width=True)
            st.success("✅ Visualization displayed successfully!")
        except Exception as e:
            st.error(f"Error displaying visualization: {e}")
            
        # Add some spacing
        st.write("")
    else:
        # Show a message if no visualization was generated
        if viz_data.get("query_result") is not None and isinstance(viz_data["query_result"], pd.DataFrame) and not viz_data["query_result"].empty:
            if "Error" not in viz_data["query_result"].columns:
                st.info("💡 No visualization was generated for this query. The data is available in the table above.")

    # Display follow-up questions if available
    if viz_data.get("follow_up_questions") and len(viz_data["follow_up_questions"]) > 0:
        st.write("---")
        st.subheader("💡 Explore Further")
        st.write("Here are some interesting follow-up questions you might want to explore:")
        
        # Create columns for the buttons
        cols = st.columns(2)
        for i, question in enumerate(viz_data["follow_up_questions"][:4]):  # Limit to 4 questions
            with cols[i % 2]:
                if st.button(question, key=f"followup_{i}", use_container_width=True):
                    st.session_state.run_query = question
                    st.rerun()
        
        # Add some spacing
        st.write("")


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
if "current_data_context" not in st.session_state:
    st.session_state.current_data_context = None
if "follow_up_questions" not in st.session_state:
    st.session_state.follow_up_questions = []
if "conversation_mode" not in st.session_state:
    st.session_state.conversation_mode = "new"  # "new" or "follow_up"

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
    with st.spinner("Generating SQL query, reviewing with GPT-4o, and analyzing your request..."):
        # Run the agent crew
        visualization_data = analyst_agents_flow(st.session_state.messages[-1]["content"])
        
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
