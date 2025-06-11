#!/usr/bin/env python3
"""
Test script for Novel Writing Agent System with Instruction Interpolation
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from novel.agent import create_agents, call_agent_async, session_service
from google.adk.runners import Runner

# Test configuration
APP_NAME = "novel_writer_interpolation_test"
USER_ID = "test_writer"
SESSION_ID = "test_session_interpolation"

async def test_instruction_interpolation():
    """Test instruction interpolation with outline and character data."""
    print("🎭 Testing Novel Writing System with Instruction Interpolation\n")
    
    # Create agents and runner
    root_agent = create_agents()
    runner = Runner(root_agent, session_service=session_service)
    
    # Initialize session with some initial data
    initial_state = {
        "novel_genre": "fantasy",
        "novel_theme": "friendship and sacrifice",
        "novel_target_length": "medium",
        "novel_outline": {
            "title": "The Crystal of Elderwood",
            "structure": {
                "act1": "Setup - Young mage discovers ancient crystal with dark power",
                "act2": "Development - Friends must choose between power and friendship",
                "act3": "Resolution - Sacrifice leads to redemption and new understanding"
            },
            "estimated_chapters": 18
        },
        "character_profiles": {
            "Lyra": {
                "role": "protagonist",
                "background": "Young fire mage from humble village",
                "personality": "Brave but impulsive, deeply loyal to friends",
                "motivation": "Protect her village and friends from ancient evil",
                "appearance": "Red hair, green eyes, burn scars on hands",
                "character_arc": "Learns that true strength comes from accepting help"
            },
            "Finn": {
                "role": "best friend",
                "background": "Earth mage, Lyra's childhood companion",
                "personality": "Cautious and wise, steady presence",
                "motivation": "Keep Lyra safe while supporting her growth",
                "appearance": "Brown hair, earth-toned clothing, calm demeanor",
                "character_arc": "Learns to trust Lyra's judgment and independence"
            }
        },
        "chapters": {}
    }
    
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        initial_state=initial_state
    )
    
    print("📊 Initial project state loaded with:")
    print(f"   Genre: {initial_state['novel_genre']}")
    print(f"   Theme: {initial_state['novel_theme']}")
    print(f"   Outline: {initial_state['novel_outline']['title']}")
    print(f"   Characters: {list(initial_state['character_profiles'].keys())}")
    
    # Test queries that should use interpolated context
    test_queries = [
        {
            "description": "📖 Check project status (should show interpolated context)",
            "query": "What's the current status of my novel project? What do you know about the story?"
        },
        {
            "description": "✨ Write opening chapter (should use interpolated outline/characters)",
            "query": "Write the opening chapter where Lyra first encounters the crystal in the Elderwood forest. Use an action hook."
        },
        {
            "description": "💬 Write dialogue chapter (should reference characters from context)",
            "query": "Write a dialogue chapter where Lyra and Finn discuss the crystal's power and what it might mean."
        },
        {
            "description": "📊 Check progress again",
            "query": "How many chapters have been written now? What should I write next?"
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
    print("🎉 Instruction Interpolation Test Complete!")
    print("✅ Agents should have access to outline and character context in their instructions")
    print(f"{'='*60}")

async def test_empty_context():
    """Test behavior when context is empty (using ? syntax)."""
    print("\n🎪 Testing Empty Context Handling\n")
    
    root_agent = create_agents()
    runner = Runner(root_agent, session_service=session_service)
    
    # Initialize session with minimal data
    empty_session_id = "empty_context_session"
    minimal_state = {
        "novel_genre": None,
        "novel_theme": None, 
        "novel_outline": {},
        "character_profiles": {},
        "chapters": {}
    }
    
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=empty_session_id,
        initial_state=minimal_state
    )
    
    print("📝 Testing with empty context (should handle gracefully with ? syntax)")
    
    await call_agent_async(
        "What do you know about my current novel project?", 
        runner, USER_ID, empty_session_id
    )

async def main():
    """Main test function."""
    try:
        # Test 1: Full context interpolation
        await test_instruction_interpolation()
        
        # Test 2: Empty context handling
        await test_empty_context()
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🏁 All interpolation tests completed.")

if __name__ == "__main__":
    asyncio.run(main()) 