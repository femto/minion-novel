from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Mock weather database
weather_db = {
    "New York": {"temperature": 72, "conditions": "sunny"},
    "London": {"temperature": 65, "conditions": "cloudy"},
    "Tokyo": {"temperature": 80, "conditions": "rainy"}
}

def get_weather(city):
    """Get weather information for a city"""
    if city in weather_db:
        return weather_db[city]
    return None

# Create agent
weather_agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description="Agent that provides weather information",
    instruction="I am a weather agent. I can tell you the weather for different cities.",
    tools=[get_weather]
)

# Set up session service and runner
session_service = InMemorySessionService()
APP_NAME = "weather_app"
USER_ID = "user123"
SESSION_ID = "session123"

session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)

runner = Runner(
    agent=weather_agent,
    app_name=APP_NAME,
    session_service=session_service
)

def main():
    # Test the weather agent
    query = "What's the weather in New York?"
    content = types.Content(
        role='user',
        parts=[types.Part(text=query)]
    )
    
    events = runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    )

    for event in events:
        if event.is_final_response():
            print(f"Agent response: {event.content.parts[0].text}")

if __name__ == "__main__":
    main() 