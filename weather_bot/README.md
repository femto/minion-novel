# Weather Bot

A sophisticated weather bot built using Google's Agent Development Kit (ADK).

## Features

- Multi-model support (Gemini, GPT-4, Claude)
- Specialized agents for greetings and farewells
- State management for user preferences
- Safety guardrails for input and tool usage
- Temperature unit conversion (Celsius/Fahrenheit)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API keys in `.env`:
```
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

3. Run the bot:
```bash
python main.py
```

## Usage

The bot can:
- Provide weather information for cities
- Handle greetings and farewells
- Remember temperature unit preferences
- Block certain keywords and cities for safety

## Architecture

- Root agent for orchestration
- Specialized sub-agents for greetings/farewells
- State management for preferences
- Input and tool usage guardrails
