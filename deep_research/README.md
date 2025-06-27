# Deep Research Agent

A comprehensive research agent that can conduct in-depth research on any topic using systematic web search and analysis.

## Features

- **Intelligent Query Generation**: Automatically generates focused research queries for any topic
- **Real Web Search**: Uses Tavily API for comprehensive web searches across multiple angles and perspectives
- **Smart Filtering**: Ranks and filters results by relevance to ensure quality
- **Professional Reports**: Generates well-structured research reports with analysis
- **Progress Tracking**: Monitors research progress through each stage

## Architecture

The Deep Research Agent follows a systematic workflow:

1. **Query Generation**: Creates 5-8 specific, focused search queries covering different aspects of the topic
2. **Information Gathering**: Performs real web searches using Tavily API for each query
3. **Content Filtering**: Uses LLM to rank and filter results by relevance to the research topic
4. **Report Generation**: Compiles findings into a comprehensive, professional research report

## Components

### Tools
- `generate_research_queries`: Creates targeted search queries
- `tavily_web_search`: Performs real web search using Tavily API
- `filter_and_rank_results`: Filters content by relevance
- `generate_research_report`: Generates final report
- `get_research_progress`: Tracks research status

### Data Models
- `ResearchQuery`: Represents individual search queries
- `ResearchResult`: Stores search result data
- `ResearchSession`: Manages entire research workflow

## Usage

### Basic Usage
```python
from deep_research.agent import create_deep_research_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Create agent and runner
agent = create_deep_research_agent()
session_service = InMemorySessionService()
runner = Runner(agent=agent, session_service=session_service)

# Conduct research
result = await runner.run_async(
    user_input="Research artificial intelligence in healthcare",
    user_id="user_123",
    session_id="session_456"
)
```

### Example Topics
- "artificial intelligence in healthcare"
- "climate change impacts on agriculture"
- "blockchain technology applications"
- "renewable energy trends 2024"
- "quantum computing developments"

## Configuration

The agent supports both Azure OpenAI and Google AI models, and requires Tavily API for web search:

### Environment Variables
```bash
# Tavily API (required for web search)
TAVILY_API_KEY=your_tavily_key

# Model selection
USE_AZURE=false  # Set to true for Azure OpenAI

# Azure OpenAI (if using)
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_key
AZURE_API_VERSION=2024-02-15-preview
AZURE_MODEL_NAME=gpt-4.1

# Google AI (if using)
GOOGLE_API_KEY=your_key
GOOGLE_MODEL_NAME=gemini-2.0-flash-exp
```

## Output Format

The research report includes:

1. **Executive Summary**: High-level overview of findings
2. **Key Findings**: Organized by themes and subtopics
3. **Detailed Analysis**: In-depth examination of the research
4. **Conclusions and Implications**: Actionable insights
5. **Sources/References**: All sources used in the research

## Recent Updates

- ✅ **Real Web Search**: Now uses Tavily API for real-time web search
- ✅ **Smart Content Filtering**: LLM-powered summarization and relevance filtering
- ✅ **Comprehensive Reports**: Professional research reports with citations

## Future Enhancements

- **Academic Sources**: Access to scholarly databases and papers
- **Multi-language Support**: Research in multiple languages
- **Export Options**: PDF, Word, and other format outputs
- **Collaborative Research**: Multi-agent research workflows
- **Advanced Search**: Integration with additional search APIs

## Testing

Run the built-in test suite:
```bash
cd deep_research
python agent.py
```

This will test the agent with several sample research topics and display the results. 