# Simple ADK Calculator Agent

# Note

You should create the `google_search_agent` directory at the root level of your project, alongside `simple_adk_agent` and `weather_bot`, not under an `app` directory.

This is a simple example of using Google's Agent Development Kit (ADK) to create a calculator agent that can perform basic arithmetic operations.

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

Try asking the agent:
- What is 5 plus 3?
- Can you multiply 7 and 6?
- Divide 10 by 2 please
- What is 15 minus 7?

## Agent Capabilities

This calculator agent can:
- Add two numbers
- Subtract two numbers
- Multiply two numbers
- Divide two numbers (with error handling for division by zero)
