#!/usr/bin/env python3
"""
Deep Research Agent Demo with Tavily Integration
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def demo_tavily_search():
    """Demonstrate the Deep Research Agent with real Tavily search"""
    
    print("🔍 Deep Research Agent Demo - Tavily Integration")
    print("=" * 60)
    
    # Check for required API keys
    if not os.getenv("TAVILY_API_KEY"):
        print("❌ Error: TAVILY_API_KEY not found in environment variables")
        print("Please set your Tavily API key to use real web search.")
        return
    
    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("AZURE_OPENAI_API_KEY"):
        print("❌ Error: No LLM API key found")
        print("Please set either GOOGLE_API_KEY or AZURE_OPENAI_API_KEY")
        return
    
    try:
        from agent import create_deep_research_agent, call_agent_async
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        
        print("✅ Creating Deep Research Agent...")
        agent = create_deep_research_agent()
        
        print("✅ Setting up session and runner...")
        session_service = InMemorySessionService()
        runner = Runner(agent=agent, session_service=session_service, app_name="demo")
        
        # Create session
        await runner.session_service.create_session(
            app_name="demo",
            user_id="demo_user",
            session_id="demo_session"
        )
        
        # Demo topics
        topics = [
            "latest developments in artificial intelligence 2024",
            "current renewable energy technologies"
        ]
        
        for i, topic in enumerate(topics, 1):
            print(f"\n🔍 Demo {i}: Researching '{topic}'")
            print("-" * 40)
            
            try:
                result = await call_agent_async(
                    query=f"Conduct comprehensive research on: {topic}",
                    runner=runner,
                    user_id="demo_user",
                    session_id="demo_session"
                )
                
                print(f"✅ Research completed!")
                print(f"📊 Result length: {len(str(result))} characters")
                print(f"📄 Preview:\n{str(result)[:200]}...")
                
            except Exception as e:
                print(f"❌ Error during research: {e}")
            
            # Pause between requests
            if i < len(topics):
                print("\n⏳ Waiting 2 seconds...")
                await asyncio.sleep(2)
        
        print(f"\n{'=' * 60}")
        print("🎉 Demo completed! The agent successfully used:")
        print("   • Tavily API for real web search")
        print("   • LLM for content summarization")
        print("   • Intelligent query generation")
        print("   • Professional report formatting")
        print("=" * 60)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(demo_tavily_search()) 