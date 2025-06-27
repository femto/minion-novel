---
title: Minion Adk
emoji: 🚀
colorFrom: red
colorTo: yellow
sdk: docker
app_port: 8000
tags:
- streamlit
pinned: false
short_description: minion-adk
license: mit
---

# Simple ADK Agent

# Note

## Setup

1. Make sure you have Python 3.11+ installed
2. Set up a virtual environment (optional but recommended):
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install the ADK:
   ```
   pip install google-adk
   ```
4. Update the API key in `simple_adk_agent/.env`:
   - Get an API key from [Google AI Studio](https://aistudio.google.com/apikey)
   - Replace `YOUR_API_KEY_HERE` with your actual API key

## Running the Agent

There are multiple ways to interact with your agent:

### 1. Using the Dev UI

Run the following command from the project root:
```
adk web
```

Then open the URL provided (usually http://localhost:8000) in your browser and select "simple_adk_agent" from the dropdown.

### 2. Using the Terminal

Run the following command:
```
adk run novel_fix
adk run deep_research
```

## Example Prompts

## Agent Capabilities

This project includes several specialized agents:

### Novel Agent (`novel/`)
- Creates detailed novel outlines based on genre, theme, and target length
- Generates comprehensive character profiles with background and motivations
- Supports both Azure OpenAI and Google AI models
- Tracks novel writing progress and chapter completion

### Novel Fix Agent (`novel_fix/`)
- Fixed pipeline for systematic novel writing
- Sequential agent workflow: parameter extraction → outline → characters → acts
- Automated chapter generation for 3-act story structure
- Optimized for consistent novel production

### Deep Research Agent (`deep_research/`)
- Conducts comprehensive research on any topic using real web search
- Intelligent query generation and Tavily API integration for current web data
- Smart filtering and ranking of research results with LLM-powered summarization
- Generates professional research reports with proper citations
- Tracks research progress through systematic workflow

## Running Individual Agents

### Novel Agent
```bash
cd novel
python agent.py
```

### Novel Fix Agent  
```bash
cd novel_fix
python agent.py
```

### Deep Research Agent
```bash
cd deep_research
python agent.py
```

## Testing Agents

Each agent includes comprehensive test suites:

```bash
# Test novel agent
cd novel
python test_interpolation.py

# Test novel fix pipeline
cd novel_fix
python test_pipeline.py

# Test deep research agent
cd deep_research
python test_research.py
```
