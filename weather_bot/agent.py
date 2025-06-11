import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

# Configure ADK to use API keys directly
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

# Model constants
MODEL_NAME = "gpt-4.1-nano"  # Azure deployment name

def create_llm():
    """Creates a LiteLLM instance configured for Azure."""
    return LiteLlm(
        model=f"azure/{MODEL_NAME}",
        api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_API_VERSION")
    )

def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """Retrieves weather, converts temp unit based on session state."""
    print(f"--- Tool: get_weather_stateful called for {city} ---")

    # Read preference from state
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius")
    print(f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # Mock weather data (always stored in Celsius internally)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # Format temperature based on state preference
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32
            temp_unit = "°F"
        else:
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        
        # Save last checked city to state
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")
        
        return result
    else:
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        print(f"--- Tool: City '{city}' not found. ---")
        return {"status": "error", "error_message": error_msg}

def say_hello(name: str = "there") -> str:
    """Provides a simple greeting."""
    print(f"--- Tool: say_hello called with name: {name} ---")
    return f"Hello, {name}!"

def say_goodbye() -> str:
    """Provides a simple farewell message."""
    print(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."

# Callbacks
def block_keyword_guardrail(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Blocks requests containing the word 'BLOCK'."""
    agent_name = callback_context.agent_name
    print(f"--- Callback: block_keyword_guardrail running for agent: {agent_name} ---")

    last_user_message_text = ""
    if llm_request.contents:
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break

    keyword_to_block = "BLOCK"
    if keyword_to_block in last_user_message_text.upper():
        print(f"--- Callback: Found '{keyword_to_block}'. Blocking LLM call! ---")
        callback_context.state["guardrail_block_keyword_triggered"] = True
        
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=f"I cannot process this request because it contains the blocked keyword '{keyword_to_block}'.")],
            )
        )
    return None

def block_paris_tool_guardrail(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext
) -> Optional[Dict]:
    """Blocks weather requests for Paris."""
    tool_name = tool.name
    agent_name = tool_context.agent_name
    print(f"--- Callback: block_paris_tool_guardrail running for tool '{tool_name}' in agent '{agent_name}' ---")

    if tool_name == "get_weather_stateful":
        city_argument = args.get("city", "")
        if city_argument and city_argument.lower() == "paris":
            print(f"--- Callback: Detected blocked city '{city_argument}'. Blocking tool execution! ---")
            tool_context.state["guardrail_tool_block_triggered"] = True
            
            return {
                "status": "error",
                "error_message": f"Policy restriction: Weather checks for '{city_argument.capitalize()}' are currently disabled."
            }
    return None

# Agent definitions
def create_agents():
    """Creates and returns the agent team."""
    # Create LLM instance
    llm = create_llm()
    
    # Greeting Agent
    greeting_agent = Agent(
        model=llm,
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )

    # Farewell Agent
    farewell_agent = Agent(
        model=llm,
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )

    # Root Agent
    root_agent = Agent(
        name="weather_agent",
        model=llm,
        description="Main agent: Handles weather, delegates greetings/farewells, includes safety guardrails.",
        instruction="You are the main Weather Agent. Provide weather using 'get_weather_stateful'. "
                   "Delegate greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                   "Handle only weather, greetings, and farewells.",
        tools=[get_weather_stateful],
        sub_agents=[greeting_agent, farewell_agent],
        output_key="last_weather_report",
        before_model_callback=block_keyword_guardrail,
        before_tool_callback=block_paris_tool_guardrail
    )

    return root_agent

async def call_agent_async(query: str, runner: Runner, user_id: str, session_id: str):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"<<< Agent Response: {event.content.parts[0].text}")
            break


session_service = InMemorySessionService()

# Create session with initial state
APP_NAME = "weather_bot"
USER_ID = "user_1"
SESSION_ID = "session_001"

initial_state = {
    "user_preference_temperature_unit": "Celsius"
}

session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
    state=initial_state
)

# Create agent and runner
root_agent = create_agents()
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service
)
async def main():
    """Main function to run the weather bot."""
    # Initialize session service
    # session_service = InMemorySessionService()
    #
    # # Create session with initial state
    # APP_NAME = "weather_bot"
    # USER_ID = "user_1"
    # SESSION_ID = "session_001"
    #
    # initial_state = {
    #     "user_preference_temperature_unit": "Celsius"
    # }
    #
    # session = session_service.create_session(
    #     app_name=APP_NAME,
    #     user_id=USER_ID,
    #     session_id=SESSION_ID,
    #     state=initial_state
    # )
    #
    # # Create agent and runner
    # root_agent = create_agents()
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    print("Weather Bot initialized! Type 'quit' to exit.")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == 'quit':
                break
                
            await call_agent_async(user_input, runner, USER_ID, SESSION_ID)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
