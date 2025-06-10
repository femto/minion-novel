import os
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Mock weather database
mock_weather_db = {
    "New York": {"temperature": 72, "condition": "sunny"},
    "London": {"temperature": 65, "condition": "cloudy"},
    "Tokyo": {"temperature": 80, "condition": "rainy"},
}

def get_weather(city: str) -> dict:
    """Get the current weather for a given city.
    
    Args:
        city: The name of the city to get weather for.
        
    Returns:
        A dictionary containing the weather information.
    """
    if city not in mock_weather_db:
        return {"error": f"Weather data not available for {city}"}
    return mock_weather_db[city]

# Define the weather agent
weather_agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description="An agent that can look up weather information for cities",
    instruction="""You are a helpful weather assistant. When asked about weather, 
    use the get_weather tool to look up the current conditions. Always provide the 
    temperature and weather condition in your response.""",
    tools=[get_weather]
)

# Create a session service
session_service = InMemorySessionService()

# Create a runner
runner = Runner(
    agent=weather_agent,
    app_name="weather_bot",
    session_service=session_service
)

async def main():
    print("Weather Agent Test")
    print("=================")
    
    # Create a session
    session_id = "test_session"
    user_id = "test_user"
    
    # Test some weather queries
    test_prompts = [
        "What's the weather like in New York?",
        "How's the weather in London?",
        "Tell me the weather in Tokyo",
        "What's the weather in Paris?"  # This should return an error
    ]
    
    for prompt in test_prompts:
        print(f"\nUser: {prompt}")
        response = await runner.run(
            input=prompt,
            user_id=user_id,
            session_id=session_id
        )
        print(f"Agent: {response}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 