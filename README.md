# 📊 Advanced Data Visualization Agent

An intelligent data visualization assistant built with Streamlit that allows users to interact with their Supabase database using natural language queries. The application leverages AI agents to understand user requests, execute SQL queries, and generate beautiful visualizatiRobust error handling ensures users always get visualizations:
1. **Primary**: AI-generated visualization using CrewAI
2. **Fallback**: Simple bar chart based on data types
3. **Graceful Degradation**: Table display with download option

## 🚀 Advanced Visualization Transformations

The system features intelligent chart transformation capabilities that automatically handle data conversions when users request different visualization types.

### 🎯 Supported Transformation Scenarios

#### 1. Bar Chart → Pie Chart (Percentage Conversion)
**User Flow:**
```
User Query: "Which car manufacturers registered the most vehicles?"
    ↓
🧠 Step 0: Understanding intent...
    → Shows "🎯 Intent: NEW_QUERY (Confidence: 95%)"
    ↓
🤖 Step 1: Generating SQL... 
    → Shows generated SQL code with professional styling
    ↓  
🔍 Step 2: Reviewing with GPT-4o...
    → Shows optimization results/comparison
    ↓
🔄 Step 3: Executing query...
    → Shows "✅ Retrieved 13 rows"
    ↓
📊 Step 4: Displaying formatted table
    → Professional pandas DataFrame with dashboard-style metrics
    → Shows key statistics: Total Records, Unique Values, Top Performer
    ↓
🎨 Step 5: Generating visualization...
    → Shows "✨ Visualization created successfully!"
    → Creates bar chart with white theme and black axis fonts
    ↓
💡 Step 6: Follow-up questions
    → Shows 4 schema-aware clickable questions
    ↓
📈 Final Result: Interactive bar chart + intelligent follow-ups

--- Follow-Up Conversation ---
User: "Convert the bar chart to pie chart"
    ↓
🧠 Intent: FOLLOW_UP (Confidence: 92%)
    ↓
🎨 Creating alternative visualization...
    → Detects chart conversion request
    → Uses target_plot_type="pie" with transformation="to_pie"
    → Automatically converts absolute values to percentages
    → Groups small categories into "Others" if needed
    ↓
✨ Alternative visualization created!
    → New pie chart with percentage labels and professional styling
    → Maintains data integrity and insights
    ↓

User: "Normalize the stacked bar plot"
    ↓
🧠 Intent: FOLLOW_UP (Confidence: 95%)
    ↓
🎨 Creating normalized visualization...
    → Applies transformation="normalize" parameter
    → Converts absolute values to percentages within each category
    → Updates y-axis to show 0-100% range with % suffix
    → Each stack now sums to 100% per category
    ↓
✨ Normalized stacked bar chart created!
    → Shows relative proportions while maintaining color grouping
    ↓
💡 Additional follow-ups generated
    → "Which regions contribute most to Toyota's sales?"
    → "Show monthly trends for top 3 manufacturers"
    → "Compare electric vs conventional vehicle registrations"
```

#### 2. Stacked Bar Chart Normalization
**User Flow:**
```
User: "Show vehicle registrations by month and manufacturer"
→ System creates stacked bar chart with absolute values

User: "Normalize the plot" or "show as percentages"
→ System automatically:
  • Applies transformation="normalize" parameter
  • Converts absolute values to percentages within each month (sums to 100%)
  • Updates y-axis to show percentage scale with % suffix
  • Maintains stacked visualization while showing relative proportions
  • Preserves color grouping and legend
```

#### 3. Advanced Chart Type Conversions
**User Flow:**
```
User: "Show quarterly sales trends"
→ System creates appropriate chart (line/bar)

User: "Convert this to a scatter plot"
→ System automatically:
  • Uses target_plot_type="scatter" with transformation="convert_chart_type"
  • Adapts data structure for scatter plot requirements
  • Maintains temporal/categorical relationships
  • Applies appropriate styling and formatting
```

#### 4. Category Consolidation (Top N + Others)
**User Flow:**
```
User: "Show all vehicle types distribution"
→ System creates chart with many categories

User: "Show only top 5 vehicle types, group the rest as Others"
→ System automatically:
  • Applies transformation="top_5" parameter
  • Identifies top N categories by value
  • Sums remaining categories into "Others"
  • Maintains total data integrity
  • Provides cleaner visualization
```

### 🤖 Intelligent Transformation Engine

The visualization tool automatically detects when data transformation is needed using advanced parameter mapping:

```python
# Example: Chart type conversion with target_plot_type parameter
def _run(self, plot_type: str, target_plot_type: str = "", transformation: str = ""):
    # Use target_plot_type if provided for chart conversion
    effective_target_type = target_plot_type if target_plot_type else plot_type
    
    # Apply intelligent transformations
    df_transformed = self._apply_intelligent_transformations(
        df, effective_target_type, current_chart_type, transformation
    )

# Example: Normalization for stacked bar charts
elif transformation == "normalize" and color_column:
    # For stacked bar plots, normalize within each x-category
    totals_per_x = df_transformed.groupby(x_column)[y_column].sum()
    for x_val in df_normalized[x_column].unique():
        total_for_x = totals_per_x[x_val]
        df_normalized.loc[mask, y_column] = (
            df_normalized.loc[mask, y_column] / total_for_x * 100
        ).round(2)

# Example: Bar to Pie transformation with target_plot_type
if current_plot_type == "bar" and target_plot_type == "pie":
    # Calculate percentages and group small categories
    total = grouped[y_column].sum()
    grouped[f'{y_column}_percentage'] = (grouped[y_column] / total * 100).round(2)
```

**Key Features:**
- **Parameter-Driven Transformations**: Uses `target_plot_type` parameter for explicit chart conversions
- **Context-Aware Processing**: Considers `current_chart_type` for optimal transformation logic
- **Smart Fallbacks**: Graceful handling when transformations aren't applicable
- **Data Integrity**: Preserves mathematical relationships and totals during transformations

### 🧪 Comprehensive Testing

The advanced transformation features are covered by extensive unit and integration tests:

- **Unit Tests**: 12+ test scenarios covering all transformation types including:
  - Chart type conversions (bar→pie, line→bar, scatter→line)
  - Normalization scenarios (stacked bar normalization, percentage conversion)
  - Parameter validation (`target_plot_type`, `transformation`, `current_chart_type`)
  - Data integrity verification (totals preservation, category grouping)
- **Integration Tests**: 8+ test scenarios for end-to-end orchestration including:
  - Full pipeline testing (SQL generation → execution → visualization)
  - Intent recognition and routing (new query vs follow-up detection)
  - Alternative visualization generation with chart conversions
  - Follow-up question generation with schema awareness
- **Manual Verification**: Real data testing with sample vehicle data
- **Performance Testing**: Separated crew architecture validation
- **Error Handling**: Graceful degradation and fallback mechanism testing

**Run tests:**
```bash
# Run comprehensive test suite
python run_advanced_tests.py

# Test specific transformation scenarios
python test_target_plot_type.py

# Test normalization functionality
python test_normalization.py
```

### 📊 User Experience Flowtomatically.

![Frontend Preview](docs/Frontend.png)

## 🚀 Features

- **Natural Language Queries**: Ask questions about your data in plain English
- **Real-time Visualization**: Automatic chart generation based on your queries
- **Interactive Chat Interface**: Conversational AI assistant for data exploration
- **Voice Input Support**: Record voice queries using built-in microphone
- **Star Schema Database**: Built-in SQLite database with vehicle market share analytics
- **Advanced Analytics**: Pre-built analytics utilities for market research
- **Data Export**: Export analysis results to CSV format
- **Responsive Design**: Modern, clean interface optimized for data analysis
- **Modular Architecture**: Well-organized codebase for easy maintenance and extension

### 🎯 Advanced Visualization Features

- **Intelligent Chart Transformations**: Advanced data transformations when switching chart types
  - **Bar → Pie**: Converts absolute values to percentages automatically using `target_plot_type="pie"`
  - **Stacked Bar Normalization**: Converts absolute values to percentages within groups using `transformation="normalize"`
  - **Line → Bar**: Aggregates time series data appropriately with smart temporal handling
  - **Any → Pie**: Calculates percentage distributions and groups small categories intelligently
  - **Chart Type Conversions**: Seamless conversions between any chart types with `target_plot_type` parameter
- **Context-Aware Follow-up Questions**: Schema-aware question generation based on current data and database structure
- **Smart Orchestration**: Advanced intent recognition that distinguishes between new queries and follow-up analysis
- **Data Transformation Engine**: Comprehensive transformation system handling:
  - Percentage conversion and normalization
  - Top-N filtering with "Others" category consolidation  
  - Category grouping and data aggregation
  - Time series formatting and aggregation
- **Memory & Chat History**: Maintains conversation context for seamless data exploration
- **Professional Styling**: Consistent white theme with black fonts across all visualizations
- **Dashboard Metrics**: Business-style metric displays with formatted numbers and trend indicators

## 🏗️ Project Structure

```
AdvancedDatavisualisationAgent/
├── 📁 backend/                    # Backend logic and services
│   └── __init__.py
├── 📁 docs/                       # Documentation and assets
│   ├── Frontend.png               # UI preview image
│   └── DATA_MODEL.md              # Star schema documentation
├── 📁 frontend/                   # Frontend components and styling
│   ├── __init__.py
│   ├── utils.py                   # CSS loading utilities
│   ├── simple_audio.py           # Voice input component
│   └── 📁 style/                  # Modular CSS files
│       ├── README.md              # CSS documentation
│       ├── base.css               # Base layout and typography
│       ├── sidebar.css            # Sidebar-specific styles
│       ├── chat.css               # Chat interface styles
│       ├── components.css         # UI components (buttons, etc.)
│       └── main.css               # Main CSS file
├── 📁 scripts/                    # Database and analytics scripts
│   ├── create_market_share_database.py  # Database creation script
│   ├── database_utils.py          # Analytics utilities
│   ├── app_integration.py         # Streamlit integration
│   └── requirements.txt           # Database dependencies
├── 📁 tests/                      # Test files
│   └── __init__.py
├── 📁 visual_agent/               # Core visualization agent logic
│   └── __init__.py
├── market_share.sqlite            # SQLite database (created by scripts)
├── app.py                         # Main Streamlit application
├── pyproject.toml                 # Poetry configuration
├── poetry.lock                    # Locked dependencies
└── README.md                      # This file
```

## 🛠️ Technologies Used

- **[Streamlit](https://streamlit.io/)** - Web application framework
- **[SQLite](https://sqlite.org/)** - Built-in analytical database
- **[Plotly](https://plotly.com/python/)** - Interactive visualization library
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation and analysis
- **[Poetry](https://python-poetry.org/)** - Dependency management
- **CSS3** - Custom styling for modern UI

## 📋 Prerequisites

- Python 3.12+
- Poetry (for dependency management)
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/AdvancedDatavisualisationAgent.git
cd AdvancedDatavisualisationAgent
```

### 2. Install Dependencies

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

### 3. Activate Virtual Environment

```bash
poetry shell
```

### 4. Set Up the Database

```bash
# Create and populate the market share database
python scripts/create_market_share_database.py

# Test the analytics utilities (optional)
python scripts/database_utils.py
```

### 5. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 🤖 AI-Powered Analytics Pipeline

### Overview

The application features a sophisticated AI-powered analytics pipeline built with **CrewAI** that provides intelligent data analysis through natural language queries. The system consists of multiple specialized AI agents working together to deliver accurate SQL generation, query optimization, and intelligent visualizations.

### 🏗️ Pipeline Architecture

The analytics pipeline is organized into **5 intelligent steps**, each providing real-time feedback to users:

#### Step 0: Intent Orchestration 🧠
- **Agent**: Conversation Orchestrator
- **Purpose**: Intelligently determines if user input is a new query or follow-up question
- **Features**:
  - Analyzes conversation context and history
  - Distinguishes between new data requests vs. follow-up questions
  - Routes to appropriate pipeline (new query or existing data discussion)
  - Real-time feedback: "🤔 Understanding your intent... 🎯 Intent: NEW_QUERY (Confidence: 95%)"

#### Step 1: SQL Generation 🤖
- **Agent**: Senior Data Analyst
- **Purpose**: Converts natural language queries into SQL
- **Features**:
  - Uses normalized star schema knowledge
  - Validates queries against available tables/columns
  - Provides detailed explanations of table usage
  - Real-time feedback: "🤖 Generating initial SQL query..."

#### Step 2: SQL Review & Optimization 🔍
- **Agent**: SQL Code Reviewer (GPT-4o)
- **Purpose**: Reviews and optimizes generated SQL for performance and correctness
- **Features**:
  - Performance optimization suggestions
  - Syntax validation and error detection
  - Query readability improvements
  - Shows before/after comparison when changes are made
  - Real-time feedback: "🔍 Reviewing SQL with GPT-4o verifier..."

#### Step 3: Query Execution 🔄
- **Purpose**: Executes the reviewed SQL query against the database
- **Features**:
  - Robust error handling with specific error messages
  - Returns formatted pandas DataFrames
  - Performance metrics (row count, execution time)
  - Data validation and quality checks
  - Real-time feedback: "🔄 Executing SQL query... ✅ Retrieved X rows"

#### Step 4: Intelligent Visualization 🎨
- **Step 4a - Data Analysis**: Data Analyst Agent (Separate Crew)
- **Step 4b - Visualization Generation**: Visualization Specialist Agent (Separate Crew)
- **Purpose**: Creates optimal visualizations based on comprehensive data analysis
- **Performance Optimization**: Agents run in separate crews for improved speed and reliability
- **Features**:
  - **Data Analysis Phase**:
    - Identifies data patterns, trends, and anomalies
    - Recommends optimal visualization types
    - Generates key insights and findings
    - Real-time feedback: "📊 Analyzing data patterns..."
  - **Visualization Generation Phase**:
    - AI-driven plot type selection based on analysis recommendations
    - Automatic column mapping (x-axis, y-axis, color grouping)
    - Smart aggregation method selection
    - Advanced transformation handling (bar→pie, percentage conversion)
    - Real-time feedback: "🎨 Creating visualization... ✨ Created successfully!"
  - **Performance Benefits**:
    - Separated crews prevent agent interference
    - Faster execution with parallel processing capability
    - Improved reliability and error isolation
    - Better resource utilization

### 🔧 Modular Function Architecture

The pipeline is implemented through modular functions for better maintainability and user feedback:

```python
# Step-by-step functions
def step_1_generate_sql(user_query: str) -> dict
def step_2_review_sql(initial_sql: str) -> dict  
def step_3_execute_query(reviewed_sql: str) -> dict
def step_4_generate_visualization(query_result: pd.DataFrame, user_query: str) -> dict
def step_4_fallback_visualization(query_result: pd.DataFrame) -> dict

# Main orchestrator
def analyst_agents_flow(user_query: str) -> dict
```

**Benefits of Modular Design:**
- ✅ **Real-Time Feedback**: Users see progress at each step
- ✅ **Independent Error Handling**: Each step can fail gracefully
- ✅ **Better Debugging**: Easier to identify and fix issues
- ✅ **Maintainability**: Single responsibility per function
- ✅ **Testability**: Each step can be tested independently

### 🧠 Intelligent Conversation Orchestration

The system features an advanced orchestration agent that provides intelligent conversation management:

#### Intent Recognition
- **Smart Context Analysis**: Understands whether users are asking new questions or following up on existing data
- **Conversation Memory**: Maintains context of previous queries and results
- **Confidence Scoring**: Provides confidence levels for intent classification

#### Follow-Up Question Capabilities
1. **Schema-Aware Suggestions**: Generates questions based on available database tables and columns
2. **Cross-Table Analysis**: Suggests opportunities to join and analyze related data
3. **Trend Analysis**: Recommends time-based queries when date columns are available
4. **Comparative Analysis**: Proposes comparisons between different entities or categories

#### Alternative Visualization Generation
- **On-Demand Chart Types**: Users can request different chart types for the same data
- **Automatic Adaptation**: Intelligently maps data to new visualization formats
- **Insight Preservation**: Maintains the analytical value while changing the presentation

#### Memory and Context Management
- **Persistent Data Context**: Remembers current query results and visualizations
- **Chat History**: Maintains conversation flow and context
- **Smart Routing**: Efficiently handles both new queries and data exploration

### 🎯 CrewAI Integration

The system uses **CrewAI** to orchestrate multiple AI agents working together:

#### Orchestration Crew
```python
orchestration_crew = Crew(
    agents=[orchestration_agent],
    tasks=[orchestration_task],
    verbose=True
)
```

#### SQL Generation Crew
```python
sql_generator_crew = Crew(
    agents=[query_generator_agent],
    tasks=[query_task],
    verbose=True
)
```

#### SQL Review Crew  
```python
sql_reviewer_crew = Crew(
    agents=[query_reviewer_agent], 
    tasks=[review_task],
    verbose=True
)
```

#### Data Analysis Crew (Performance Optimized)
```python
data_analysis_crew = Crew(
    agents=[data_analyst_agent],
    tasks=[data_analysis_task],
    verbose=True
)
```

#### Data Visualization Crew (Performance Optimized)
```python
data_visualization_crew = Crew(
    agents=[visualization_agent],
    tasks=[visualization_task],
    verbose=True
)
```

**Performance Note**: Data analysis and visualization are now separated into individual crews to prevent agent interference and improve execution speed. This architecture change resulted in significantly faster processing times and better reliability.

#### Follow-Up Question Crew
```python
follow_up_crew = Crew(
    agents=[orchestration_agent],
    tasks=[follow_up_questions_task],
    verbose=True
)
```

#### Data Question Answering Crew
```python
data_question_crew = Crew(
    agents=[orchestration_agent],
    tasks=[data_question_answering_task],
    verbose=True
)
```

#### Alternative Visualization Crew
```python
alternative_viz_crew = Crew(
    agents=[visualization_agent],
    tasks=[alternative_visualization_task],
    verbose=True
)
```

### 📊 Intelligent Visualization System

#### DataFrameVisualizationTool
The system includes a custom visualization tool with advanced chart conversion capabilities:
- **Multi-Parameter Architecture**: Supports `plot_type`, `target_plot_type`, `transformation`, and `current_chart_type` parameters
- **Intelligent Chart Conversions**: Uses `target_plot_type` for seamless chart type transformations
- **Smart Data Transformations**: Automatically handles data preprocessing when converting between chart types
- **JSON Specification Output**: Generates Plotly-compatible JSON specifications with proper styling
- **Normalization Engine**: Advanced normalization for stacked bar charts (converts to percentages within groups)
- **Fallback Mechanisms**: Robust error handling with graceful degradation
- **White Theme Integration**: Consistent professional styling with black fonts and white backgrounds

#### Plot Type Selection Guidelines
The AI agents follow sophisticated guidelines for choosing optimal visualizations:

- **Bar Charts**: Categorical comparisons, rankings, counts by category
- **Line Charts**: Time series, trends over sequential data  
- **Scatter Plots**: Relationships between continuous variables
- **Pie Charts**: Proportions/percentages (≤6 categories)
- **Histograms**: Distribution of continuous variables
- **Box Plots**: Distribution analysis, outlier detection
- **Heatmaps**: Correlation analysis, 2D density data

#### Fallback Mechanisms
Robust error handling ensures users always get visualizations:
1. **Primary**: AI-generated visualization using CrewAI
2. **Fallback**: Simple bar chart based on data types
3. **Graceful Degradation**: Table display with download option

### � User Experience Flow

```
User Query: "Which car manufacturers registered the most vehicles?"
    ↓
� Step 0: Understanding intent...
    → Shows "🎯 Intent: NEW_QUERY (Confidence: 95%)"
    ↓
�🤖 Step 1: Generating SQL... 
    → Shows generated SQL code
    ↓  
🔍 Step 2: Reviewing with GPT-4o...
    → Shows optimization results/comparison
    ↓
🔄 Step 3: Executing query...
    → Shows "✅ Retrieved 13 rows"
    ↓
📊 Step 4: Displaying formatted table
    → Professional pandas DataFrame display
    ↓
🎨 Step 5: Generating visualization...
    → Shows "✨ Visualization created successfully!"
    ↓
� Step 6: Follow-up questions
    → Shows 4 schema-aware clickable questions
    ↓
�📈 Final Result: Interactive bar chart + intelligent follow-ups

--- Follow-Up Conversation ---
User: "Convert the bar chart to pie chart"
    ↓
🧠 Intent: FOLLOW_UP (Confidence: 92%)
    ↓
🎨 Creating alternative visualization...
    → Detects bar→pie transformation needed
    → Automatically converts absolute values to percentages
    → Groups small categories into "Others" if needed
    ↓
✨ Alternative visualization created!
    → New pie chart with percentage labels
    → Maintains data integrity and insights
    ↓
💡 Additional follow-ups generated
    → "Which regions contribute most to Toyota's sales?"
    → "Show monthly trends for top 3 manufacturers"
    → "Compare electric vs conventional vehicle registrations"
```

### 🛠️ Configuration Files

The AI agents are configured through YAML files for easy customization:

#### agents.yaml
```yaml
query_generator_agent:
  role: Senior Data Analyst
  goal: Generate accurate SQL queries from natural language
  backstory: Expert in star schema design and SQL optimization

visualization_agent:
  role: Data Visualization Specialist  
  goal: Create optimal visualizations for data insights
  backstory: Expert in data visualization best practices
```

#### tasks.yaml
```yaml
data_analysis_task:
  description: Analyze DataFrame and provide visualization recommendations
  expected_output: Comprehensive analysis with chart type suggestions

visualization_task:
  description: Create optimal visualization using DataFrame Visualization Tool
  expected_output: Complete plot specification with accurate data mapping
```

### 🧪 Testing & Validation

The pipeline includes comprehensive testing:

```python
# Test individual steps
result = step_1_generate_sql("Which manufacturers have most vehicles?")
assert result["success"] == True
assert "SELECT" in result["initial_sql"]

# Test full pipeline
response = analyst_agents_flow("Show vehicle registrations by brand")
assert response["plotly_figure"] is not None
assert isinstance(response["query_result"], pd.DataFrame)
```

### 📈 Performance Optimizations

1. **Smart Aggregation**: Only aggregates when necessary
2. **Efficient Data Handling**: Direct DataFrame to JSON conversion
3. **Caching**: Schema and configuration caching for faster responses
4. **Parallel Processing**: Multiple agents work simultaneously when possible
5. **Resource Management**: Proper error handling prevents resource leaks

### 🔧 Advanced Features

#### Error Recovery
- **SQL Generation Failures**: Provides detailed error explanations
- **Query Execution Errors**: Shows specific database error messages  
- **Visualization Failures**: Falls back to simple charts automatically
- **Network Issues**: Graceful degradation with offline capabilities

#### Data Validation
- **Schema Compliance**: Validates queries against available tables
- **Data Type Checking**: Ensures appropriate column usage
- **Result Validation**: Checks for empty results and data quality
- **Security**: SQL injection prevention through parameterized queries

### 📋 Getting Started with AI Pipeline

1. **Install Dependencies**:
```bash
poetry install
```

2. **Configure AI Agents**:
```bash
# Edit configuration files
vim agents/config/agents.yaml
vim agents/config/tasks.yaml
```

3. **Test Individual Steps**:
```python
from app import step_1_generate_sql, step_2_review_sql

# Test SQL generation
result = step_1_generate_sql("Show top manufacturers")
print(result)

# Test SQL review
review = step_2_review_sql(result["initial_sql"])
print(review)
```

4. **Run Full Pipeline**:
```bash
streamlit run app.py
```

The AI pipeline provides a seamless, intelligent analytics experience that transforms natural language into actionable data insights with professional visualizations.

### Getting Started

1. **Launch the App**: The interface consists of a sidebar chat panel and a main visualization area
2. **Ask Questions**: Use the chat input, voice recording, or click one of the suggested prompts:
   - "Show me top brands by market share"
   - "What are the fuel type trends?"
   - "Compare luxury vs economy brands"
   - "Show quarterly performance"
3. **View Results**: The AI agent will process your query and display interactive visualizations

### Sample Queries

Try asking questions like:
- **Basic Analysis**: "What are the top-selling vehicle brands?"
- **Market Trends**: "Show me market share trends by fuel type"
- **Comparative Analysis**: "Compare electric vs gasoline vehicle sales"
- **Specific Brand Focus**: "Which models are performing best for Toyota?"
- **Time-based Analysis**: "What's the quarterly revenue breakdown?"
- **Technical Specifications**: "Show transmission preferences by brand"

**Chart Transformation Requests:**
- **Type Conversions**: "Convert this to a pie chart" | "Change to a line chart" | "Make this a scatter plot"
- **Normalization**: "Normalize the plot" | "Show as percentages" | "Convert to normalized stacked bars"
- **Data Simplification**: "Show only top 5 categories" | "Group small categories as Others"
- **Style Changes**: "Make this chart look more professional" | "Add trend lines"

## 🎨 UI Components

### Sidebar Chat Interface
- **Chat History**: Displays conversation with timestamps and role indicators
- **Input Box**: Natural language query input with professional black border styling
- **Voice Input**: Record audio queries using the microphone button (simple_audio.py)
- **Real-time Updates**: Immediate response to user queries with step-by-step progress
- **Professional Styling**: Consistent CSS theming with modular style files

### Main Visualization Area
- **Dashboard Metrics**: Business-style metric cards showing key statistics
  - Total Records count with formatting
  - Unique Values identification  
  - Top Performer highlighting with trend indicators
- **Professional Data Tables**: Enhanced pandas DataFrame display with:
  - White background and black text for readability
  - Proper column formatting and alignment
  - Export capabilities for further analysis
- **Interactive Charts**: Plotly visualizations with:
  - Consistent white theme and black axis fonts
  - Professional color palette
  - Responsive design for different screen sizes
  - Hover tooltips and interactive elements
- **Follow-up Questions**: Clickable question buttons that:
  - Generate based on current data context
  - Leverage database schema for intelligent suggestions
  - Maintain conversation flow and context
- **SQL Code Display**: Formatted SQL queries with:
  - Syntax highlighting and professional presentation
  - Before/after comparison for optimized queries
  - Copy-to-clipboard functionality
- **Welcome Screen**: Guided introduction with sample prompts
- **Dynamic Charts**: Interactive Plotly visualizations
- **Research Insights**: Contextual information from RAG pipeline

### Styling Features
- **Modular CSS**: Organized styling in separate files
- **Responsive Design**: Adapts to different screen sizes
- **Modern Aesthetics**: Clean, professional appearance
- **Color-coded Elements**: Intuitive visual hierarchy

## �️ Database & Analytics

### Market Share Database

The application includes a comprehensive SQLite database with vehicle market share data:

- **Star Schema Design**: Optimized for analytical queries
- **Dimension Tables**: Brands, Models, Fuel Types, Transmissions, Time
- **Fact Table**: Vehicle Market Share with units sold, revenue, and market share percentages
- **Sample Data**: Pre-populated with realistic automotive industry data

### Analytics Capabilities

The `scripts/` directory contains powerful analytics utilities:

#### Database Creation
```bash
python scripts/create_market_share_database.py
```
Creates the complete database schema and populates it with sample data.

#### Analytics Utilities
```bash
python scripts/database_utils.py
```
Provides various analytical functions:
- Top brands by market share
- Market share trends over time
- Fuel type analysis
- Model performance metrics
- Quarterly summaries
- Geographic analysis by country

#### Streamlit Integration
```python
from scripts.app_integration import MarketShareIntegration

integration = MarketShareIntegration()
chart_data = integration.get_chart_data_for_streamlit()
```

### Data Export

Export your analysis results:
- Full market share data to CSV
- Brand performance summaries
- Fuel type analysis reports
- Custom filtered datasets

## �🔧 Configuration

### Environment Setup

Create a `.env` file in the project root for configuration:

```env
# Supabase Configuration (when integrated)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Other API keys
OPENAI_API_KEY=your_openai_key
```

### CSS Customization

The UI styling is organized in modular CSS files:

- `base.css` - Core layout and typography
- `sidebar.css` - Chat interface styling
- `chat.css` - Message and input styling
- `components.css` - Buttons and UI elements

## 🧪 Development

### Project Architecture

The application follows a modular architecture:

1. **Frontend Layer** (`frontend/`): UI components and styling
2. **Backend Layer** (`backend/`): Data processing and API integration
3. **Visualization Layer** (`visual_agent/`): Chart generation logic
4. **Main App** (`app.py`): Streamlit application entry point

### Adding New Features

1. **New CSS Styles**: Add to appropriate CSS file in `frontend/style/`
2. **Backend Logic**: Implement in `backend/` modules
3. **UI Components**: Create reusable functions in `frontend/utils.py`
4. **Tests**: Add test cases in `tests/` directory

### CSS Development

The project uses a modular CSS approach. To add new styles:

1. Choose the appropriate CSS file or create a new one
2. Add the file to the CSS loading list in `app.py`
3. Document changes in `frontend/style/README.md`

## 🧪 Testing & Validation

The project includes comprehensive testing for advanced visualization transformations and orchestration capabilities.

### Running Tests

#### Advanced Visualization Tests
Test the intelligent chart transformation and orchestration features:

```bash
# Run all advanced tests (recommended)
python run_advanced_tests.py

# Run only unit tests for transformations
python run_advanced_tests.py --skip-integration

# Run only integration tests for orchestration
python run_advanced_tests.py --skip-manual
```

#### Test Coverage

**Transformation Scenarios Tested:**
- ✅ Bar Chart → Pie Chart (with percentage conversion)
- ✅ Absolute Values → Percentage Display
- ✅ Line Chart → Bar Chart (time series aggregation)
- ✅ Category Consolidation (Top N + Others grouping)
- ✅ Context-aware Follow-up Question Generation
- ✅ Orchestration Decision Making
- ✅ End-to-End Integration Testing

**Test Results Example:**
```
🚀 Advanced Data Visualization Agent - Test Suite
================================================================================
🧪 PHASE 1: Unit Tests - Visualization Transformations
✅ Scenario 1 PASSED: Bar to Pie conversion with 8 categories
✅ Scenario 2 PASSED: Percentage conversion with total sum check
✅ Scenario 3 PASSED: Time series to bar conversion with 6 periods
✅ Scenario 4 PASSED: Category consolidation with 8 final categories
✅ Scenario 5 PASSED: Top N filtering with Others grouping

🔗 PHASE 2: Integration Tests - Orchestration Pipeline
✅ Bar to Pie Chart Orchestration Flow PASSED
✅ Percentage Conversion Scenario PASSED
✅ Top N with Others Scenario PASSED
✅ Follow-up Question Generation PASSED

🎯 PHASE 3: Manual Scenario Verification
✅ Bar to Pie transformation: SUCCESS
✅ Data integrity: 5 categories preserved
✅ Value transformation: Numeric values generated

📋 COMPREHENSIVE TEST REPORT
================================================================================
Overall Result: 🎉 ALL TESTS PASSED
🚀 READY FOR DEPLOYMENT
```

#### Individual Test Files

```bash
# Test specific components
python -m pytest tests/test_advanced_visualizations.py -v
python -m pytest tests/test_orchestration_integration.py -v

# Test database functionality
python -m pytest tests/test_database.py -v
python -m pytest tests/test_sql_crew.py -v
```

### Validation Features

- **Unit Tests**: Verify individual transformation logic
- **Integration Tests**: Test end-to-end orchestration flows
- **Manual Verification**: Real data testing with sample datasets
- **Error Handling**: Comprehensive fallback mechanism testing
- **Performance Testing**: Transformation speed and accuracy validation


## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-username/AdvancedDatavisualisationAgent/issues) page
2. Create a new issue with detailed description
3. Contact the development team

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [Plotly](https://plotly.com/) for powerful visualization capabilities
- [Supabase](https://supabase.com/) for database infrastructure
- The open-source community for inspiration and tools

---

**Built with ❤️ for better data visualization experiences**
