#!/usr/bin/env python3
"""
ADK Web Service integration for Novel Fix system.
Provides web interface for the fixed workflow novel writing pipeline.
"""

import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.web import start_web_service
from novel_fix.agent import create_root_agent

# Create session service and root agent
session_service = InMemorySessionService()

# Create the root agent (simplified SequentialAgent approach)
root_agent = create_root_agent()

async def setup_web_service():
    """Set up and start the ADK web service for Novel Fix."""
    print("🚀 Starting Novel Fix ADK Web Service")
    print("📚 System: Fixed Workflow Novel Writing Pipeline")
    print("🌐 Access the web interface at the URL shown below")
    print("=" * 50)
    
    # Start the web service
    await start_web_service(
        app_name="novel_fix",
        agent=root_agent,
        session_service=session_service,
        port=8000
    )

if __name__ == "__main__":
    asyncio.run(setup_web_service()) 