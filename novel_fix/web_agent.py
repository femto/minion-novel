#!/usr/bin/env python3
"""
Novel Fix Web Agent - Dedicated agent for ADK Web service
"""
import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Import our agent structure
from agent import create_root_agent

# Load environment variables
load_dotenv()

# Configure ADK to use API keys directly
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

# Constants for Web Service
APP_NAME = "novel_fix_web"
DEFAULT_USER_ID = "web_user"

# Create session service and root agent
session_service = InMemorySessionService()
root_agent = create_root_agent()

async def setup_web_service():
    """Setup the web service with default session."""
    # Create a runner for web service
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service
    )
    
    # Create default session
    session_id = "default_web_session"
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=DEFAULT_USER_ID,
        session_id=session_id
    )
    
    print(f"✅ Novel Fix Web Service Ready!")
    print(f"📱 App Name: {APP_NAME}")
    print(f"👤 Default User: {DEFAULT_USER_ID}")
    print(f"🔗 Session: {session_id}")
    print("🌐 Ready for ADK Web integration...")
    
    return runner

async def test_web_agent():
    """Test the web agent functionality."""
    print("🧪 Testing Novel Fix Web Agent")
    print("=" * 50)
    
    runner = await setup_web_service()
    
    # Test queries
    test_queries = [
        "Hello! What is Novel Fix?",
        "How does the fixed workflow differ from dynamic novel writing?",
        "Start a mystery novel about betrayal and trust, short length",
        "What's the current status of my projects?"
    ]
    
    session_id = "default_web_session"
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 40)
        
        content = types.Content(role='user', parts=[types.Part(text=query)])
        
        async for event in runner.run_async(
            user_id=DEFAULT_USER_ID, 
            session_id=session_id, 
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    response = event.content.parts[0].text
                    print(f"🤖 Response: {response[:200]}...")
                break
        
        await asyncio.sleep(0.5)  # Brief pause between tests

if __name__ == "__main__":
    print("🌐 Novel Fix Web Agent")
    print("Ready for ADK Web integration")
    print("Use 'adk web' command to start web interface")
    
    # Run test
    asyncio.run(test_web_agent()) 