# Advanced Data Visualization Agent: An AI-Powered Natural Language Database Interface

## Abstract

This report presents the development and implementation of an Advanced Data Visualization Agent, a sophisticated web-based application that bridges the gap between natural language queries and database interaction. The system leverages artificial intelligence technologies to enable non-technical users to interact with complex SQLite databases through conversational interfaces, automatically generating appropriate SQL queries and corresponding data visualizations. 

The application implements a Star Schema database design containing UK vehicle registration data spanning 2023-2024, with over 625,000 records across multiple dimensional tables. The system integrates multiple state-of-the-art AI services including OpenAI's language models for SQL generation, IBM Watson's speech-to-text and text-to-speech services, and ElevenLabs' advanced audio synthesis technology.

Key innovations include a hybrid visualization system that achieves 95.6% latency reduction compared to traditional agent-based approaches, multi-modal input support through voice and text interfaces, and intelligent conversation management that distinguishes between new queries and follow-up questions. The system demonstrates practical applications in business intelligence, data analytics, and educational environments where database expertise may be limited.

## 1. Introduction

### 1.1 Background and Motivation

In the contemporary data-driven business environment, the ability to extract meaningful insights from databases is crucial for informed decision-making. However, traditional database interaction methods require specialized SQL knowledge, creating a significant barrier for non-technical stakeholders who need to access and analyze data. This technical gap often results in delayed decision-making processes, increased dependency on technical teams, and underutilization of valuable data assets.

The emergence of Large Language Models (LLMs) and natural language processing technologies has opened new possibilities for democratizing database access. By enabling natural language interfaces to structured data, organizations can empower a broader range of users to independently explore and analyze their data assets.

### 1.2 Problem Statement

The primary challenge addressed by this project is the creation of an intelligent, user-friendly interface that can:

1. **Translate natural language queries into accurate SQL statements** while understanding complex database schemas and relationships
2. **Generate appropriate visualizations automatically** based on the nature of the data and query intent
3. **Support multi-modal interaction** including voice input and audio output for enhanced accessibility
4. **Maintain conversation context** to enable follow-up questions and iterative data exploration
5. **Ensure high performance and reliability** suitable for production business environments

### 1.3 Research Objectives

This project aims to develop and evaluate a comprehensive solution that addresses the following objectives:

- **Primary Objective**: Design and implement a natural language interface for SQLite databases that enables non-technical users to perform complex data analysis tasks
- **Secondary Objectives**:
  - Develop a robust SQL generation pipeline using AI agents with validation and optimization capabilities
  - Create an efficient visualization system that automatically selects appropriate chart types based on data characteristics
  - Integrate multi-modal interfaces supporting both voice and text input/output
  - Implement conversation management for contextual follow-up queries
  - Evaluate system performance, accuracy, and user experience metrics

### 1.4 Scope and Limitations

The scope of this project encompasses:

- Development of a web-based application using Streamlit framework
- Implementation of a Star Schema database containing UK vehicle registration data
- Integration of multiple AI services (OpenAI, IBM Watson, ElevenLabs)
- Creation of comprehensive evaluation frameworks for system performance
- Documentation and testing procedures for production deployment

**Limitations**:
- The system is currently designed for SQLite databases with Star Schema architecture
- Voice recognition accuracy depends on audio quality and background noise
- API dependencies on external services may affect system availability
- Current implementation focuses on analytical queries rather than transactional operations

### 1.5 Report Structure

This report is organized into the following sections: Section 2 presents the related work and theoretical background; Section 3 details the system architecture and design methodology; Section 4 describes the implementation approach and technical components; Section 5 presents evaluation results and performance metrics; Section 6 discusses findings, lessons leanred, and future work; and Section 7 concludes with a summary of contributions and implications.

## Section 2: Related Work 

<to be completed>

## 3. System Architecture and Design Methodology 

### 3.1 Application Design

The system architecture follows a modular design pattern built on the Streamlit framework, enabling rapid development and deployment of interactive web applications. The application employs a multi-tier architecture consisting of presentation, business logic, and data access layers.

The presentation layer provides a responsive web interface with dual input modalities (text and voice) and unified output formats (visual charts and audio responses). The business logic layer orchestrates AI agents for query processing, implements conversation state management, and coordinates between natural language processing and database operations. The data access layer manages SQLite database connections and executes optimized SQL queries against the Star Schema.

Key architectural decisions include the implementation of session state management for conversation continuity, modular component design for maintainability, and API abstraction layers for external service integration (OpenAI, IBM Watson, ElevenLabs).

### 3.2 Database Design

The database implementation utilizes a Traditional Star Schema design optimized for analytical workloads and Business Intelligence queries. This design pattern separates dimensional data from factual measurements, enabling efficient aggregation operations and simplified query construction for AI agents.

**Dimensional Structure:**
- **Fact Table**: FactRegisteredVehicles (625,476 records) containing vehicle registration measurements with foreign key references
- **Time Dimension**: DimTime (24 records) providing temporal attributes including quarters, months, and formatted date strings
- **Geographic Dimensions**: DimGeographyCountry (9 records) and DimGeographyDistrict (2,778 records) for spatial analysis
- **Business Dimensions**: DimOEM (14 records) for manufacturer data and DimVehicle (29 records) for vehicle characteristics

The schema design incorporates referential integrity constraints, indexed foreign key relationships for optimal join performance, and denormalized attributes to reduce query complexity. This structure enables the AI agents to generate efficient SQL queries while maintaining data consistency and supporting complex analytical operations.

### 3.3 CrewAI Agents Design

The system implements a multi-agent architecture using the CrewAI framework, where specialized AI agents collaborate to process natural language queries and generate database interactions. This approach leverages the principle of separation of concerns, assigning specific responsibilities to individual agents.

#### 3.3.1 Agent Descriptions: Roles and Tasks

**SQL Generator Agent**: Responsible for translating natural language queries into syntactically correct SQL statements. This agent utilizes domain-specific knowledge about the database schema and applies pattern recognition to identify query intent and required table joins.

**SQL Reviewer Agent**: Functions as a quality assurance mechanism, analyzing generated SQL queries for optimization opportunities, syntax validation, and logical correctness. This agent implements a secondary validation layer to ensure query accuracy and performance.

**Orchestration Agent**: Manages conversation flow by distinguishing between new data requests and follow-up questions, maintaining conversation context, and routing queries to appropriate processing pipelines.

**Visualization Agents**: Specialized agents for chart type selection and data presentation, including both the original data visualization crew and the optimized chart type crew for the hybrid visualization system.

#### 3.3.2 Database Domain Knowledge Integration

The agents incorporate comprehensive database schema knowledge through a structured configuration approach stored in `config.yaml` as `db_schema_agent`. This knowledge base includes:

- Complete table structures with column definitions, data types, and sample values
- Foreign key relationships and join patterns for optimal query construction
- Business logic rules for data filtering and aggregation
- Query optimization guidelines and performance considerations

This domain knowledge enables agents to understand complex relationships between entities, generate appropriate WHERE clauses for data filtering, and construct efficient JOIN operations across multiple dimensional tables.

#### 3.3.3 Pydantic Integration for Output Reliability

The system employs Pydantic models to ensure structured, validated outputs from AI agents. This design pattern addresses the inherent variability in LLM responses by enforcing strict output schemas and data validation rules.

Pydantic models define expected output formats for SQL queries, visualization parameters, and agent responses, providing automatic type checking, data validation, and error handling. This approach significantly improves system reliability by catching malformed outputs before they propagate to downstream components, ensuring consistent API contracts between agents, and enabling robust error recovery mechanisms.

## 4. Implementation Approach

### 4.1 Core Pipeline - 5-Step Process

The system implements a sequential processing pipeline that transforms natural language queries into database insights through five distinct phases:

**Step 1 - Intent Orchestration (`orchestrate_user_intent`)**: Analyzes user input to determine query classification (new request vs. follow-up question) using conversation history and current data context. This step enables intelligent conversation management and appropriate response routing.

**Step 2 - SQL Generation (`step_1_generate_sql`)**: Employs the SQL Generator Agent to convert natural language queries into initial SQL statements using domain knowledge and schema understanding.

**Step 3 - SQL Review (`step_2_review_sql`)**: Utilizes the SQL Reviewer Agent to validate, optimize, and refine generated queries, ensuring syntactic correctness and performance optimization.

**Step 4 - Query Execution (`step_3_execute_query`)**: Executes validated SQL queries against the SQLite database with comprehensive error handling and result validation.

**Step 5 - Visualization Generation (`step_4_generate_visualization`)**: Creates appropriate data visualizations using the hybrid visualization system, automatically selecting chart types based on data characteristics and user intent.

### 4.2 Initial Visualization Workflow - Agent-Based Approach

The original visualization implementation employed a `data_visualization_crew` consisting of multiple AI agents for chart generation. This approach utilized:

- **Data Analysis Agent**: Analyzed query results to identify data patterns and visualization opportunities
- **Chart Type Selection Agent**: Determined appropriate visualization types based on data characteristics
- **Plotly Generation Agent**: Created interactive charts using natural language descriptions

While this approach provided high-quality visualizations, performance analysis revealed significant latency issues with average response times of 6.5 seconds due to multiple LLM API calls and complex agent coordination.

### 4.3 Hybrid Visualization Workflow - Optimized Approach

To address performance limitations, the system was redesigned with a hybrid approach combining heuristic-based selection with selective AI integration:

**Analytics Selector Component**: Implements rule-based chart type selection using keyword detection and data pattern analysis. This component identifies common visualization scenarios (time series, market share, distribution analysis) without requiring LLM calls.

**Plot Builder Component**: Provides deterministic Plotly figure generation from structured chart specifications, supporting multiple chart types (bar, line, pie, scatter, histogram, box plots) with consistent styling.

**LLM Fallback Mechanism**: Maintains AI agent capability for complex visualization scenarios that cannot be resolved through heuristic approaches.

This hybrid approach achieved a 95.6% latency reduction (from 6.5 seconds to 0.287 seconds) while maintaining visualization quality and expanding chart type support.

### 4.4 Speech-to-Text Integration

The system incorporates dual speech-to-text services to maximize accessibility and transcription accuracy across different use cases:

**OpenAI Whisper Integration**: Provides robust multilingual support with offline processing capabilities. The implementation handles audio file format conversion, manages API request/response cycles, and includes confidence scoring for transcription quality assessment.

**IBM Watson Speech-to-Text Integration**: Offers enterprise-grade transcription with real-time processing capabilities and domain-specific model support. This service provides detailed confidence metrics and supports custom vocabulary for improved accuracy in specialized domains.

The voice input interface implements automatic silence detection, visual feedback during recording, transcription editing capabilities, and service selection options. Error handling mechanisms ensure graceful degradation when services are unavailable.

### Section 4.5: Text-to-Speech Integration



