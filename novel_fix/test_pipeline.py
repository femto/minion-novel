#!/usr/bin/env python3
"""
Simple test for novel_fix pipeline
"""
import asyncio
import sys
import os

# Add the parent directory to Python path to import the agent module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from novel_fix.agent import create_and_run_novel

async def test_short_novel():
    """Test creating a short novel"""
    print("🧪 Testing Novel Fix Pipeline")
    print("=" * 50)
    
    try:
        # Test a short sci-fi novel
        await create_and_run_novel(
            genre="science fiction",
            theme="artificial intelligence and humanity",
            target_length="short"
        )
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_short_novel()) 