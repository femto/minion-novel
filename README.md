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
adk run simple_adk_agent
```

### 3. Using the Test Script

Run the test script to see some example interactions:
```
python test_calculator.py
```

## Example Prompts

## Agent Capabilities
