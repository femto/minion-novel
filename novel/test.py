#!/usr/bin/env python3
"""
Test script for the Novel Writing Agent System
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from novel.agent import create_agents, call_agent_async, session_service
from google.adk.runners import Runner

# Test configuration
APP_NAME = "novel_writer_test"
USER_ID = "test_writer"
SESSION_ID = "test_session_001"

async def test_novel_writing_system():
    """Test the complete novel writing system."""
    print("🎭 Starting Novel Writing Agent System Test\n")
    
    # Create agents and runner
    root_agent = create_agents()
    runner = Runner(root_agent, session_service=session_service)
    
    # Initialize session
    initial_state = {
        "novel_genre": None,
        "novel_theme": None,
        "novel_target_length": None,
        "novel_outline": {},
        "character_profiles": {},
        "chapters": {}
    }
    
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        initial_state=initial_state
    )
    
    # Test queries to demonstrate the system
    test_queries = [
        {
            "description": "📖 Creating a novel outline",
            "query": "Help me create an outline for a fantasy novel about courage and sacrifice. The target length should be medium."
        },
        {
            "description": "👥 Creating character profiles", 
            "query": "Create character profiles for a brave young warrior protagonist named Aria and a wise mentor character named Elder Thane."
        },
        {
            "description": "✨ Writing an opening chapter",
            "query": "Write an opening chapter set in an ancient forest, introducing Aria with an action hook where she discovers a mysterious artifact."
        },
        {
            "description": "⚔️ Writing an action chapter",
            "query": "Write an action chapter with a magical battle between Aria and shadow creatures, high intensity conflict."
        },
        {
            "description": "💬 Writing a dialogue chapter",
            "query": "Write a dialogue chapter where Aria and Elder Thane discuss the artifact's power, revealing its dangerous history."
        },
        {
            "description": "📊 Checking progress",
            "query": "What's my current progress on the novel? How many chapters have been written?"
        }
    ]
    
    # Execute test queries
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {test_case['description']}")
        print(f"{'='*60}")
        
        await call_agent_async(test_case['query'], runner, USER_ID, SESSION_ID)
        
        # Add a brief pause between tests
        await asyncio.sleep(2)
    
    print(f"\n{'='*60}")
    print("🎉 Novel Writing System Test Complete!")
    print(f"{'='*60}")

async def test_chapter_agents_individually():
    """Test each chapter writing agent individually."""
    print("\n🎪 Testing Individual Chapter Agents\n")
    
    from novel.chapter_agents import create_chapter_agents
    
    # Create the act agent (which contains all chapter sub-agents)
    act_agent = create_chapter_agents()
    runner = Runner(act_agent, session_service=session_service)
    
    # Initialize a separate session for individual testing
    test_session_id = "chapter_test_session"
    initial_state = {
        "novel_genre": "fantasy",
        "novel_theme": "heroism",
        "character_profiles": {
            "Aria": {"role": "protagonist", "name": "Aria"},
            "Thane": {"role": "mentor", "name": "Elder Thane"}
        }
    }
    
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=test_session_id,
        initial_state=initial_state
    )
    
    # Test each chapter type
    chapter_tests = [
        {
            "type": "Opening Chapter",
            "query": "Write an opening chapter set in a magical academy, introducing Aria with a dialogue hook about her mysterious past."
        },
        {
            "type": "Action Chapter", 
            "query": "Write an action chapter with a dragon fight, medium intensity conflict, involving both Aria and Thane."
        },
        {
            "type": "Dialogue Chapter",
            "query": "Write a dialogue chapter for character development between Aria and Thane, revealing Aria's true heritage."
        },
        {
            "type": "Climax Chapter",
            "query": "Write a climax chapter with a magical confrontation, resolution through sacrifice, reaching emotional peak of triumph."
        }
    ]
    
    for test in chapter_tests:
        print(f"\n📝 Testing {test['type']}")
        print("-" * 40)
        await call_agent_async(test['query'], runner, USER_ID, test_session_id)
        await asyncio.sleep(1.5)

async def main():
    """Main test function."""
    try:
        # Test 1: Complete system test
        await test_novel_writing_system()
        
        # Test 2: Individual chapter agents
        await test_chapter_agents_individually()
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🏁 All tests completed.")

if __name__ == "__main__":
    asyncio.run(main()) 