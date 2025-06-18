import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService, Session
from google.adk.memory import InMemoryMemoryService # Import MemoryService
from google.adk.runners import Runner
from google.adk.tools import load_memory # Tool to query memory
from google.genai.types import Content, Part
from google.adk.models.lite_llm import LiteLlm

# Load environment variables from .env file
load_dotenv()

# --- Constants ---
APP_NAME = "memory_example_app"
USER_ID = "mem_user"

USE_AZURE = os.getenv("USE_AZURE", "false").lower() == "true"
AZURE_MODEL_NAME = os.getenv("AZURE_MODEL_NAME", "gpt-4.1")
GOOGLE_MODEL_NAME = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.0-flash")

# Create LLM instance based on environment
if USE_AZURE:
    MODEL = LiteLlm(
        model=f"azure/{AZURE_MODEL_NAME}",
        api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_API_VERSION")
    )
else:
    MODEL = GOOGLE_MODEL_NAME

# --- Agent Definitions ---
# Agent 1: Simple agent to capture information
info_capture_agent = LlmAgent(
    model=MODEL,
    name="InfoCaptureAgent",
    instruction="Acknowledge the user's statement.",
    # output_key="captured_info" # Could optionally save to state too
)

# Agent 2: Agent that can use memory
memory_recall_agent = LlmAgent(
    model=MODEL,
    name="MemoryRecallAgent",
    instruction="Answer the user's question. Use the 'load_memory' tool "
                "if the answer might be in past conversations.",
    tools=[load_memory] # Give the agent the tool
)

# --- Services and Runner ---
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService() # Use in-memory for demo

runner = Runner(
    # Start with the info capture agent
    agent=info_capture_agent,
    app_name=APP_NAME,
    session_service=session_service,
    memory_service=memory_service # Provide the memory service to the Runner
)

async def main():
    # --- Scenario ---

    # Turn 1: Capture some information in a session
    print("--- Turn 1: Capturing Information ---")
    session1_id = "session_info"
    session1 = await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)
    user_input1 = Content(parts=[Part(text="My favorite project is Project Alpha.")], role="user")

    # Run the agent
    final_response_text = "(No final response)"
    async for event in runner.run_async(user_id=USER_ID, session_id=session1_id, new_message=user_input1):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_text = event.content.parts[0].text
    print(f"Agent 1 Response: {final_response_text}")

    # Get the completed session
    completed_session1 = await runner.session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)

    # Add this session's content to the Memory Service
    print("\n--- Adding Session 1 to Memory ---")
    result = await memory_service.add_session_to_memory(completed_session1)
    print("Session added to memory.")

    # Turn 2: In a *new* (or same) session, ask a question requiring memory
    print("\n--- Turn 2: Recalling Information ---")
    session2_id = "session_recall" # Can be same or different session ID
    session2 = await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session2_id)

    # Switch runner to the recall agent
    runner.agent = memory_recall_agent
    user_input2 = Content(parts=[Part(text="What is my favorite project?")], role="user")

    # Run the recall agent
    print("Running MemoryRecallAgent...")
    final_response_text_2 = "(No final response)"
    async for event in runner.run_async(user_id=USER_ID, session_id=session2_id, new_message=user_input2):
        print(f"  Event: {event.author} - Type: {'Text' if event.content and event.content.parts and event.content.parts[0].text else ''}"
            f"{'FuncCall' if event.get_function_calls() else ''}"
            f"{'FuncResp' if event.get_function_responses() else ''}")
        if event.is_final_response() and event.content and event.content.parts:
            final_response_text_2 = event.content.parts[0].text
            print(f"Agent 2 Final Response: {final_response_text_2}")
            break # Stop after final response

if __name__ == "__main__":
    asyncio.run(main())