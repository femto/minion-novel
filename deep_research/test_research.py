#!/usr/bin/env python3
"""
Test script for Deep Research Agent
Tests the research workflow with various topics
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deep_research.agent import create_deep_research_agent, call_agent_async
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

async def test_research_workflow():
    """Test the complete research workflow."""
    print("=" * 80)
    print("DEEP RESEARCH AGENT TEST")
    print("=" * 80)
    
    # Create agent and runner
    agent = create_deep_research_agent()
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, session_service=session_service, app_name="deep_research_test")
    
    # Test cases with different complexity levels
    test_cases = [
        {
            "topic": "artificial intelligence in healthcare",
            "description": "AI/ML applications in medical field"
        },
        {
            "topic": "sustainable energy storage solutions",
            "description": "Green technology and battery innovations"
        },
        {
            "topic": "remote work productivity tools 2024",
            "description": "Current workplace technology trends"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'-' * 60}")
        print(f"Test Case {i}: {test_case['topic']}")
        print(f"Description: {test_case['description']}")
        print(f"{'-' * 60}")
        
        try:
            # Create session first
            session_id = f"test_session_{i}"
            await runner.session_service.create_session(
                app_name="deep_research_test",
                user_id="test_user",
                session_id=session_id
            )
            
            # Run research
            result = await call_agent_async(
                query=f"Conduct comprehensive research on: {test_case['topic']}",
                runner=runner,
                user_id="test_user",
                session_id=session_id
            )
            
            print(f"\n✓ Research completed for: {test_case['topic']}")
            print(f"Result length: {len(str(result))} characters")
            
            # Show first 500 characters of result
            result_preview = str(result)[:500]
            print(f"\nResult preview:\n{result_preview}...")
            
        except Exception as e:
            print(f"\n✗ Error in test case {i}: {str(e)}")
    
    print(f"\n{'=' * 80}")
    print("RESEARCH TESTING COMPLETE")
    print(f"{'=' * 80}")

async def test_individual_tools():
    """Test individual research tools."""
    print("\n" + "=" * 80)
    print("INDIVIDUAL TOOLS TEST")
    print("=" * 80)
    
    # Create agent
    agent = create_deep_research_agent()
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, session_service=session_service, app_name="tools_test")
    
    test_topic = "blockchain technology applications"
    
    # Test sequence
    test_commands = [
        f"Generate research queries for the topic: {test_topic}",
        f"Search for information about: {test_topic}",
        f"Filter and rank the research results for relevance to: {test_topic}",
        f"Generate a comprehensive research report on: {test_topic}",
        "Show me the current research progress"
    ]
    
    session_id = "tool_test_session"
    
    # Create session first
    await runner.session_service.create_session(
        app_name="tools_test",
        user_id="tool_test_user",
        session_id=session_id
    )
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{'-' * 40}")
        print(f"Tool Test {i}: {command}")
        print(f"{'-' * 40}")
        
        try:
            result = await call_agent_async(
                query=command,
                runner=runner,
                user_id="tool_test_user",
                session_id=session_id
            )
            
            print(f"✓ Command executed successfully")
            print(f"Result: {str(result)[:200]}...")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")

async def test_error_handling():
    """Test error handling and edge cases."""
    print("\n" + "=" * 80)
    print("ERROR HANDLING TEST")
    print("=" * 80)
    
    agent = create_deep_research_agent()
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, session_service=session_service, app_name="error_test")
    
    # Test edge cases
    edge_cases = [
        "",  # Empty query
        "x",  # Very short query
        "a" * 1000,  # Very long query
        "研究人工智能",  # Non-English query
        "What is 2+2?",  # Simple question that doesn't need research
    ]
    
    for i, query in enumerate(edge_cases, 1):
        print(f"\n{'-' * 40}")
        print(f"Edge Case {i}: '{query[:50]}{'...' if len(query) > 50 else ''}'")
        print(f"{'-' * 40}")
        
        try:
            # Create session first
            session_id = f"edge_session_{i}"
            await runner.session_service.create_session(
                app_name="error_test",
                user_id="edge_test_user",
                session_id=session_id
            )
            
            result = await call_agent_async(
                query=f"Research: {query}" if query else "Research something",
                runner=runner,
                user_id="edge_test_user",
                session_id=session_id
            )
            
            print(f"✓ Handled gracefully")
            print(f"Result: {str(result)[:100]}...")
            
        except Exception as e:
            print(f"✗ Error (expected): {str(e)}")

async def main():
    """Run all tests."""
    print("Starting Deep Research Agent Testing Suite...")
    
    try:
        # Run test suites
        await test_research_workflow()
        await test_individual_tools()
        await test_error_handling()
        
        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nFatal error in test suite: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 