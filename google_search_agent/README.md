# Google Search Agent

This is an example of using Google's Agent Development Kit (ADK) to create a search agent that can answer questions using Google Search.

## Setup

1. Make sure you have Python 3.9+ installed
2. Set up a virtual environment (optional but recommended):
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install the ADK:
   ```
   pip install google-adk
   ```
4. Update the API keys in `google_search_agent/.env`:
   - Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
   - Get a Google Search API key from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Create a Custom Search Engine and get the Engine ID from [Google Programmable Search Engine](https://programmablesearchengine.google.com/controlpanel/create)
   - Replace the placeholder values with your actual keys and IDs

## Running the Agent

There are multiple ways to interact with your agent:

### 1. Using the Dev UI

Run the following command from the project root:
```
adk web
```

Then open the URL provided (usually http://localhost:8000) in your browser and select "google_search_agent" from the dropdown.

### 2. Using the Terminal

Run the following command:
```
adk run google_search_agent
```

### 3. Using the Test Script

Run the test script to see some example interactions:
```
python test_search_agent.py
```

## Example Prompts

Try asking the agent:
- What is the capital of France?
- Who won the last FIFA World Cup?
- What are the latest developments in AI?
- What is the weather like in Tokyo today?
- Tell me about the history of the internet.

## Agent Capabilities

This search agent can:
- Search the web for information using Google Search
- Provide factual answers to questions
- Cite sources for the information it provides
