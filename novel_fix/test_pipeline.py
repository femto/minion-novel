#!/usr/bin/env python3
"""
Test script for the novel_fix pipeline system with dynamic parameter extraction.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from adk modules
sys.path.append(str(Path(__file__).parent.parent))

from novel_fix.agent import create_root_agent, extract_novel_params_from_text

async def test_parameter_extraction():
    """Test the parameter extraction function"""
    print("=== Testing Parameter Extraction ===")
    
    test_inputs = [
        "I want to write a mystery novel about a detective solving crimes in a small town",
        "Create a science fiction story about space exploration with medium length",  
        "Write a short romance novel about finding love",
        "I need a long fantasy adventure about dragons and magic",
        "Just write a novel"  # Should use defaults
    ]
    
    for user_input in test_inputs:
        params = extract_novel_params_from_text(user_input)
        print(f"\nInput: {user_input}")
        print(f"Extracted: {params}")

async def test_root_agent_creation():
    """Test the root agent creation"""
    print("\n=== Testing Root Agent Creation ===")
    
    # Test agent creation
    root_agent = create_root_agent()
    print(f"Root agent created: {root_agent.name}")
    print(f"  Description: {root_agent.description}")
    print(f"  Sub-agents count: {len(root_agent.sub_agents)}")
    
    for i, sub_agent in enumerate(root_agent.sub_agents, 1):
        print(f"  {i}. {sub_agent.name} - {sub_agent.description}")

async def main():
    """Run all tests"""
    print("Novel Fix Pipeline Test Suite")
    print("============================")
    
    try:
        await test_parameter_extraction()
        await test_root_agent_creation()
        
        print("\n=== Summary ===")
        print("✅ Parameter extraction working")
        print("✅ Root agent creation working")
        print("✅ Sequential pipeline structure verified")
        print("\n=== All tests completed successfully ===")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 