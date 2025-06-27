#!/usr/bin/env python3
"""
Example usage of Deep Research Agent
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def example_research():
    """Example of using the Deep Research Agent"""
    
    # Check if we have the required dependencies
    try:
        from agent import create_deep_research_agent, call_agent_async
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
    except ImportError as e:
        print(f"Missing dependencies: {e}")
        print("Please install: pip install google-adk python-dotenv google-generativeai litellm")
        return
    
    print("=" * 60)
    print("DEEP RESEARCH AGENT - EXAMPLE USAGE")
    print("=" * 60)
    
    # Create the agent
    print("Creating Deep Research Agent...")
    agent = create_deep_research_agent()
    
    # Set up session and runner
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, session_service=session_service, app_name="deep_research_example")
    
    # Example research topics
    topics = [
        "artificial intelligence in healthcare",
        "renewable energy storage technologies",
        "blockchain applications in finance"
    ]
    
    for i, topic in enumerate(topics, 1):
        print(f"\n{'-' * 40}")
        print(f"Example {i}: Researching '{topic}'")
        print(f"{'-' * 40}")
        
        try:
            # Create session first
            session_id = f"example_session_{i}"
            await runner.session_service.create_session(
                app_name="deep_research_example", 
                user_id="example_user", 
                session_id=session_id
            )
            
            # Conduct research
            result = await call_agent_async(
                query=f"Conduct comprehensive research on: {topic}",
                runner=runner,
                user_id="example_user",
                session_id=session_id
            )
            
            print(f"✓ Research completed!")
            print(f"Result preview (first 300 characters):")
            print(f"{str(result)[:300]}...")
            
        except Exception as e:
            print(f"✗ Error during research: {e}")
        
        # Add a small delay between requests
        await asyncio.sleep(1)
    
    print(f"\n{'=' * 60}")
    print("EXAMPLE COMPLETED")
    print(f"{'=' * 60}")

async def interactive_research():
    """Interactive research session"""
    
    try:
        from agent import create_deep_research_agent, call_agent_async
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
    except ImportError as e:
        print(f"Missing dependencies: {e}")
        return
    
    print("\n" + "=" * 60)
    print("INTERACTIVE RESEARCH SESSION")
    print("=" * 60)
    print("Enter a research topic (or 'quit' to exit)")
    
    # Create agent and runner
    agent = create_deep_research_agent()
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, session_service=session_service, app_name="interactive_research")
    
    session_id = "interactive_session"
    
    while True:
        try:
            topic = input("\nResearch topic: ").strip()
            
            if topic.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not topic:
                print("Please enter a valid topic.")
                continue
            
            print(f"\nConducting research on: {topic}")
            print("This may take a moment...")
            
            # Create session if not exists
            try:
                await runner.session_service.create_session(
                    app_name="interactive_research",
                    user_id="interactive_user", 
                    session_id=session_id
                )
            except:
                pass  # Session might already exist
            
            result = await call_agent_async(
                query=f"Research: {topic}",
                runner=runner,
                user_id="interactive_user",
                session_id=session_id
            )
            
            print(f"\n{'=' * 40}")
            print("RESEARCH RESULTS")
            print(f"{'=' * 40}")
            print(result)
            print(f"{'=' * 40}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

async def main():
    """Main function"""
    print("Deep Research Agent Examples")
    print("1. Automated examples")
    print("2. Interactive research")
    
    try:
        choice = input("\nSelect option (1 or 2): ").strip()
        
        if choice == "1":
            await example_research()
        elif choice == "2":
            await interactive_research()
        else:
            print("Invalid choice. Running automated examples...")
            await example_research()
            
    except KeyboardInterrupt:
        print("\nGoodbye!")

if __name__ == "__main__":
    asyncio.run(main()) 