# 📊 Advanced Data Visualization Agent

A sophisticated Streamlit application that enables users to interact with their SQLite database using natural language queries. The system intelligently queries data from a Star Schema formatted database and displays both tabular results and suitable visualizations for each request. Users can interact with the system through text or voice input, and receive responses in both text and audio formats.

![Visualization Agent Interface](docs/Frontend.png)

## 🎯 General App Description

This application provides an AI-powered interface for database interaction and visualization. The core functionality includes:

### **Core Pipeline - 5-Step Process**

The application follows a sophisticated pipeline to process user queries:

1. **`orchestrate_user_intent`** - Determines whether the user query is a new data request or a follow-up question about existing data
2. **`step_1_generate_sql`** - Generates initial SQL queries using CrewAI agents based on natural language input
3. **`step_2_review_sql`** - Reviews and optimizes SQL queries using GPT-4o for accuracy and performance
4. **`step_3_execute_query`** - Executes the validated SQL query against the SQLite database
5. **`step_4_generate_visualization`** - Creates appropriate visualizations using the hybrid visualization system

### **Key Features**

- **Natural Language to SQL**: Convert conversational queries into optimized SQL
- **Comprehensive Multi-Modal Input**: Support for text input and dual speech-to-text services (IBM Watson/OpenAI Whisper)
- **Triple Audio Output**: Text-to-speech responses using IBM Watson, ElevenLabs, and OpenAI TTS services
- **Smart Visualization**: Automatic chart type selection and generation
- **Conversation Memory**: Context-aware follow-up question handling
- **Database Schema Intelligence**: Understanding of Star Schema relationships for optimal queries

## 🗄️ SQLite Database & Star Schema

### **Database Structure**

The application uses a SQLite database with a **Traditional Star Schema** design optimized for analytical queries:

- **Database Type**: SQLite
- **Schema Design**: Star Schema with fact and dimension tables
- **Data Coverage**: UK Vehicle Registration Data (2023-2024)
- **Total Records**: 625,476 fact records
- **Time Granularity**: Monthly data across 24 months

### **Star Schema Components**

#### **Dimension Tables**
1. **DimTime** (24 records) - Temporal dimension with quarters and year-month attributes
2. **DimOEM** (14 records) - Vehicle manufacturers with categorization (Luxury, Premium, Mass Market)
3. **DimVehicle** (29 records) - Vehicle characteristics combining body type and fuel type
4. **DimGeographyCountry** (9 records) - Country-level geography with ISO codes
5. **DimGeographyDistrict** (2,778 records) - District-level geography with hierarchical location paths

#### **Fact Table**
- **FactRegisteredVehicles** (625,476 records) - Core measurements with foreign keys to all dimensions

### **Schema Benefits**
- **Optimized for Analytics**: Fast aggregation and filtering operations
- **Referential Integrity**: All foreign key relationships properly maintained
- **Performance**: Indexed joins for optimal query execution
- **Scalability**: Design supports additional time periods and geographic regions

## 🎤 Speech-to-Text Integration

The application supports dual speech-to-text services for maximum flexibility and accuracy:

### **OpenAI Whisper**
- **Global Coverage**: Support for 100+ languages
- **High Accuracy**: State-of-the-art speech recognition
- **Offline Capability**: Can process audio locally
- **Integration**: Seamless integration with OpenAI ecosystem

### **IBM Watson Speech-to-Text**
- **Enterprise Grade**: Built for business applications
- **Confidence Scoring**: Provides transcription confidence metrics
- **Real-time Processing**: Fast, reliable transcription
- **Custom Models**: Supports domain-specific vocabulary

### **Voice Input Features**
- **Automatic Recording**: Voice activity detection with 2-second silence cutoff
- **Visual Feedback**: Real-time waveform display during recording
- **Edit Capability**: Review and edit transcriptions before submission
- **Service Selection**: Choose between IBM Watson and OpenAI Whisper
- **Quality Indicators**: Confidence scores and transcription quality metrics

## 🔊 Text-to-Speech Integration

Audio response capabilities using three premium TTS services:

### **IBM Watson Text-to-Speech**
- **Voice Options**: 6 professional voices (3 male, 3 female)
- **Enterprise Quality**: High-fidelity audio synthesis
- **Multiple Languages**: Support for various accents and languages
- **SSML Support**: Advanced speech synthesis markup
- **Voices Include**:
  - Kevin (Male, US English)
  - Michael (Male, US English) 
  - Allison (Female, US English)
  - Lisa (Female, US English)
  - Emily (Female, US English)
  - Henry (Male, US English)

### **ElevenLabs AI Speech**
- **Premium Voices**: High-quality AI-generated speech
- **Natural Intonation**: Emotionally expressive audio
- **Voice Cloning**: Custom voice creation capabilities
- **Multiple Voices**: Professional and conversational options
- **Real-time Streaming**: Low-latency audio generation

### **OpenAI Text-to-Speech**
- **Latest TTS Technology**: Advanced neural text-to-speech synthesis
- **7 Voice Options**: Diverse selection including Alloy, Echo, Fable, Onyx, Nova, Shimmer, and Nova
- **Custom Instructions**: Personalized speaking style and tone control
- **Streaming API**: Real-time audio generation for immediate playback
- **High Quality**: Professional-grade audio output with natural intonation
- **4,096 Character Limit**: Efficient processing of extended text responses

### **Audio Features**
- **Unified Interface**: Single control panel for all three services
- **Voice Selection**: Dropdown menus for voice customization across all providers
- **Enable/Disable Toggle**: Easy control over audio responses
- **Session Memory**: Remembers user preferences across sessions
- **Error Handling**: Graceful fallbacks when services are unavailable
- **Provider Selection**: Choose between IBM Watson, ElevenLabs, and OpenAI TTS

## 📈 Visualization Module

### **Hybrid Visualization System**

The application uses a sophisticated hybrid approach for chart generation:

#### **Architecture Components**

1. **Analytics Selector** (`frontend/analytics_selector.py`)
   - Heuristic-based chart type selection
   - Keyword detection for specific analysis types (market share, time series, distribution)
   - LLM fallback for complex scenarios
   - ChartPlan model for deterministic plot specifications

2. **Plot Builder** (`frontend/plot_builder.py`)
   - Deterministic Plotly figure generation
   - Support for multiple chart types: bar, stacked bar, line, pie, scatter, histogram, box
   - Data transformations: percentage conversion, normalization, top-N filtering
   - Consistent white theme styling

3. **Hybrid Integration** (`frontend/hybrid_visualization.py`)
   - Seamless integration between analytics selector and plot builder
   - Alternative visualization support for follow-up requests
   - Performance optimization with 95.6% latency reduction

#### **Supported Chart Types**
- **Bar Charts**: Categorical comparisons and rankings
- **Line Charts**: Time series trends and temporal analysis
- **Pie Charts**: Proportional data and market share visualization
- **Stacked Bar Charts**: Multi-dimensional categorical data
- **Scatter Plots**: Correlation and relationship analysis
- **Histograms**: Distribution analysis
- **Box Plots**: Statistical distribution visualization

#### **Performance Metrics**
- **Average Latency**: 0.287 seconds (vs 6.5 seconds with agent-based approach)
- **LLM Calls**: 0-1 calls (vs 3-4 calls previously)
- **Success Rate**: Deterministic and consistent
- **Chart Quality**: Maintained high quality with rule-based + LLM fallback

### **Visualization Features**
- **Automatic Chart Selection**: AI determines the most appropriate visualization type
- **Interactive Charts**: Plotly-based interactive visualizations
- **Responsive Design**: Charts adapt to different screen sizes
- **Custom Styling**: Consistent white theme with professional appearance
- **Data Insights**: Automatic generation of key findings and insights
- **Alternative Views**: Users can request different chart types for the same data

## 🛠️ Installation & Setup

### **Prerequisites**
- Python 3.8+
- SQLite database with Star Schema
- IBM Cloud account (for IBM services)
- OpenAI API key (for Whisper and TTS)
- ElevenLabs API key (for TTS)

### **Environment Variables**
```bash
export OPENAI_API_KEY="your_openai_key"
export IBM_TEXT_TO_SPEECH_KEY="your_ibm_tts_key"
export IBM_SPEECH_TO_TEXT_KEY="your_ibm_stt_key"
export ELEVENLABS_API_KEY="your_elevenlabs_key"
```

### **Installation**
```bash
# Clone repository
git clone https://github.com/john2408/AdvancedDatavisualisationAgent
cd AdvancedDatavisualisationAgent

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

## 📁 Project Structure

```
AdvancedDatavisualisationAgent/
├── app.py                          # Main Streamlit application
├── config.yaml                     # Configuration settings
├── agents/                         # CrewAI agents for SQL generation and review
├── backend/                        # Database utilities and SQL execution
├── frontend/                       # UI components and visualization modules
│   ├── hybrid_visualization.py     # Hybrid visualization system
│   ├── analytics_selector.py       # Chart type selection logic
│   ├── plot_builder.py            # Plotly figure generation
│   ├── ibm_speech_text.py         # IBM Watson Speech-to-Text
│   ├── ibm_text_speech.py         # IBM Watson Text-to-Speech
│   ├── elevenlabs_text_speech.py  # ElevenLabs TTS integration
│   ├── openai_text_speech.py      # OpenAI Text-to-Speech integration
│   └── voice_components.py        # OpenAI Whisper integration
├── data/                           # SQLite database and data files
├── docs/                           # Documentation and guides
├── tests/                          # Comprehensive test suite
└── scripts/                       # Database setup and ETL scripts
```

## 🚀 Usage Examples

### **Natural Language Queries**
- "Show me the top 10 car manufacturers by registration volume"
- "What are the monthly registration trends for BMW versus Mercedes?"
- "Which electric vehicles were registered most in England in 2024?"
- "Compare hybrid vehicle adoption across different UK regions"

### **Voice Queries**
- Use the microphone button to record voice queries
- Speak naturally and clearly
- Review transcription before submitting
- Edit if needed for accuracy

### **Follow-up Questions**
- "Show this as a pie chart instead"
- "What about the data for Scotland?"
- "Can you break this down by quarter?"
- "Show me the same analysis for electric vehicles"

## 🧪 Testing & Evaluation

The application includes comprehensive evaluation systems:

- **SQL Agent Accuracy Evaluation**: Measures query generation accuracy with 100-point scoring system
- **App Latency Evaluation**: Monitors performance across the 4-step pipeline
- **Visualization Testing**: Unit tests for all chart types and data transformations
- **Voice Integration Testing**: Validation of speech-to-text and text-to-speech functionality

## 📊 Performance Metrics

- **Query Generation**: ~3.2 seconds average
- **Query Review**: ~2.7 seconds average  
- **Query Execution**: ~0.3 seconds average
- **Visualization**: ~1.1 seconds average
- **Total Pipeline**: ~7.3 seconds average end-to-end
- **Success Rate**: 100% for tested scenarios

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Additional Resources

- [Database Schema Reference](docs/DATABASE_SCHEMA_REFERENCE.md)
- [Voice Input Guide](docs/VOICE_INPUT_GUIDE.md)
- [IBM Text-to-Speech Implementation](docs/IBM_TEXT_TO_SPEECH_IMPLEMENTATION.md)
- [Star Schema Implementation](docs/STAR_SCHEMA_IMPLEMENTATION_SUMMARY.md)
- [Evaluation Systems Summary](EVALUATION_SYSTEMS_SUMMARY.md)