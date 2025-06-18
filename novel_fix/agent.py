import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent, Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from typing import Optional, Dict, Any, List
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure ADK to use API keys directly
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

# Model constants
USE_AZURE = os.getenv("USE_AZURE", "false").lower() == "true"
AZURE_MODEL_NAME = os.getenv("AZURE_MODEL_NAME", "gpt-4.1")
GOOGLE_MODEL_NAME = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.0-flash-exp")

def create_llm():
    """Creates a LLM instance based on environment configuration."""
    if USE_AZURE:
        return LiteLlm(
            model=f"azure/{AZURE_MODEL_NAME}",
            api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_API_VERSION")
        )
    else:
        return GOOGLE_MODEL_NAME

# ===== TOOLS FOR PIPELINE CONTROL =====

async def run_fixed_pipeline(genre: str, theme: str, target_length: str, tool_context: ToolContext) -> dict:
    """Tool to run the complete fixed novel writing pipeline."""
    print(f"--- Tool: run_fixed_pipeline called for {genre} novel about {theme} ---")
    
    # Save pipeline parameters to state
    tool_context.state["pipeline_genre"] = genre
    tool_context.state["pipeline_theme"] = theme
    tool_context.state["pipeline_target_length"] = target_length
    tool_context.state["pipeline_status"] = "running"
    
    # Create the pipeline agent
    pipeline_agent = create_novel_pipeline_agent(genre, theme, target_length)
    
    # Note: In a real implementation, you'd want to run this asynchronously
    # For now, we'll just indicate that the pipeline has been set up
    tool_context.state["pipeline_agent"] = "configured"
    tool_context.state["pipeline_status"] = "ready"
    
    return {
        "status": "success",
        "message": f"Fixed pipeline configured for {genre} novel about {theme} (length: {target_length})",
        "steps": [
            "1. Outline Creation",
            "2. Character Development", 
            "3. Act 1 Writing (4 chapters)",
            "4. Act 2 Writing (6 chapters)",
            "5. Act 3 Writing (4 chapters)"
        ]
    }

async def get_pipeline_status(tool_context: ToolContext) -> dict:
    """Gets the current status of the fixed pipeline."""
    print(f"--- Tool: get_pipeline_status called ---")
    
    pipeline_status = tool_context.state.get("pipeline_status", "not_started")
    pipeline_genre = tool_context.state.get("pipeline_genre", "N/A")
    pipeline_theme = tool_context.state.get("pipeline_theme", "N/A")
    pipeline_target_length = tool_context.state.get("pipeline_target_length", "N/A")
    
    return {
        "status": pipeline_status,
        "genre": pipeline_genre,
        "theme": pipeline_theme,
        "target_length": pipeline_target_length,
        "pipeline_type": "Fixed Sequential Workflow"
    }

# ===== WORKFLOW AGENTS FOR FIXED PIPELINE =====

def create_novel_pipeline_agent(genre: str, theme: str, target_length: str = "medium") -> SequentialAgent:
    """
    Creates a SequentialAgent that executes the novel writing pipeline in fixed order:
    1. Outline Creation
    2. Character Development  
    3. Act 1 Writing (with chapters)
    4. Act 2 Writing (with chapters)
    5. Act 3 Writing (with chapters)
    """
    llm = create_llm()
    
    # Step 1: Outline Agent
    outline_agent = LlmAgent(
        model=llm,
        name="OutlineAgent",
        instruction=f"""You are the Outline Creation Agent for a {genre} novel with theme '{theme}' and target length '{target_length}'.

Create a comprehensive novel outline that includes:
1. Novel Title
2. Three-Act Structure:
   - Act 1 (Setup): 25% of story - Character introduction, world-building, inciting incident
   - Act 2 (Development): 50% of story - Rising action, conflicts, character development, midpoint crisis
   - Act 3 (Resolution): 25% of story - Climax, falling action, resolution
3. Chapter breakdown for each act:
   - Short novel (~50k words): 4+6+4 = 14 chapters
   - Medium novel (~80k words): 6+8+6 = 20 chapters
   - Long novel (~120k words): 8+10+8 = 26 chapters
4. Key plot points and turning points
5. Character arcs and theme development
6. Chapter summaries with specific events

Provide a detailed, structured outline that will guide the entire writing process.""",
        description=f"Creates comprehensive outline for {genre} novel about {theme}",
        output_key="novel_outline"
    )
    
    # Step 2: Character Development Agent
    character_agent = LlmAgent(
        model=llm,
        name="CharacterAgent", 
        instruction=f"""You are the Character Development Agent. Based on the outline: {{novel_outline}}, create detailed character profiles.

Create comprehensive character profiles for:
1. Main Protagonist - detailed background, motivation, arc
2. Main Antagonist - complex villain with clear motivation
3. 2-3 Supporting Characters - each with distinct roles and personalities

For each character include:
- Full name, age, appearance
- Personality traits and quirks
- Background and personal history
- Goals, motivations, fears
- Skills and abilities
- Character arc throughout the story
- Relationships with other characters
- How they serve the theme of '{theme}'
- Role in each act of the story

Ensure characters fit the {genre} genre and support the established outline.""",
        description="Develops detailed character profiles based on the outline",
        output_key="character_profiles"
    )
    
    # Determine chapter counts based on target length
    if target_length.lower() == "short":
        act1_chapters, act2_chapters, act3_chapters = 4, 6, 4
    elif target_length.lower() == "long":
        act1_chapters, act2_chapters, act3_chapters = 8, 10, 8
    else:  # medium
        act1_chapters, act2_chapters, act3_chapters = 6, 8, 6
    
    # Step 3: Act 1 Agent (Setup)
    act1_agent = create_act_writing_agent(1, "Setup", llm, act1_chapters)
    
    # Step 4: Act 2 Agent (Development) 
    act2_agent = create_act_writing_agent(2, "Development", llm, act2_chapters)
    
    # Step 5: Act 3 Agent (Resolution)
    act3_agent = create_act_writing_agent(3, "Resolution", llm, act3_chapters)
    
    # Create the Sequential Pipeline Agent
    pipeline_agent = SequentialAgent(
        name="NovelWritingPipeline",
        description=f"Fixed pipeline for writing {genre} novel about {theme}",
        sub_agents=[
            outline_agent,
            character_agent, 
            act1_agent,
            act2_agent,
            act3_agent
        ]
    )
    
    return pipeline_agent

def create_act_writing_agent(act_number: int, act_name: str, llm, chapter_count: int) -> SequentialAgent:
    """Creates a Sequential Agent for writing all chapters in a specific act."""
    
    # Determine chapter focus based on act
    if act_number == 1:
        chapter_focus = "character introduction, world-building, inciting incident"
    elif act_number == 2:
        chapter_focus = "rising action, conflicts, character development, midpoint crisis"
    else:  # Act 3
        chapter_focus = "climax preparation, climax, falling action, resolution"
    
    # Create chapter writing agents for this act
    chapter_agents = []
    for chapter_num in range(1, chapter_count + 1):
        chapter_agent = LlmAgent(
            model=llm,
            name=f"Act{act_number}Chapter{chapter_num}Agent",
            instruction=f"""You are the Chapter Writing Agent for Act {act_number}, Chapter {chapter_num} of {chapter_count}.

CONTEXT:
- Act: {act_name} (Act {act_number})
- Chapter: {chapter_num} of {chapter_count} in this act
- Focus: {chapter_focus}
- Outline: {{novel_outline}}
- Characters: {{character_profiles}}

Your task is to write Chapter {chapter_num} of Act {act_number}:

1. Follow the outline structure for this specific chapter
2. Use the established characters with their personalities and arcs
3. Write 1000-1500 words of compelling narrative
4. Include dialogue, action, and description as appropriate
5. Advance the plot according to the act's purpose ({chapter_focus})
6. Maintain consistency with previous chapters
7. End with appropriate transition or hook for next chapter

Chapter Requirements for Act {act_number}:
{f"- Introduce main character and world" if act_number == 1 else ""}
{f"- Present the inciting incident" if act_number == 1 and chapter_num >= 3 else ""}
{f"- Develop conflicts and relationships" if act_number == 2 else ""}
{f"- Build to midpoint crisis" if act_number == 2 and chapter_num >= chapter_count - 2 else ""}
{f"- Prepare for climax" if act_number == 3 and chapter_num == 1 else ""}
{f"- Present the climax" if act_number == 3 and chapter_num == 2 else ""}
{f"- Resolve conflicts" if act_number == 3 and chapter_num >= 3 else ""}

Write the complete chapter content.""",
            description=f"Writes Chapter {chapter_num} of Act {act_number} ({act_name})",
            output_key=f"act{act_number}_chapter{chapter_num}"
        )
        chapter_agents.append(chapter_agent)
    
    # Create Sequential Agent for this act
    act_agent = SequentialAgent(
        name=f"Act{act_number}Agent",
        description=f"Writes all chapters for Act {act_number}: {act_name}",
        sub_agents=chapter_agents
    )
    
    return act_agent

# ===== ROOT AGENT CREATION =====

def create_root_agent():
    """Creates the root agent for novel_fix with interactive capabilities."""
    llm = create_llm()

    return create_novel_pipeline_agent(genre, theme, target_length)
    
    # Pipeline Control Agent
    pipeline_controller = Agent(
        model=llm,
        name="pipeline_controller",
        instruction="""You are the Pipeline Controller for the Novel Fix system.

You manage the FIXED WORKFLOW novel writing pipeline that follows this exact sequence:
1. Outline Creation
2. Character Development
3. Act 1 Writing (multiple chapters)
4. Act 2 Writing (multiple chapters) 
5. Act 3 Writing (multiple chapters)

When users want to start a fixed pipeline, use the 'run_fixed_pipeline' tool.
When users ask about pipeline status, use the 'get_pipeline_status' tool.

This is different from the dynamic novel writing system - here the workflow is predetermined and automatic.""",
        description="Controls the fixed workflow pipeline execution",
        tools=[run_fixed_pipeline, get_pipeline_status],
    )
    
    # Root Agent that coordinates everything
    root_agent = Agent(
        name="novel_fix_agent",
        model=llm,
        description="Novel Fix - Fixed Workflow Novel Writing System: Uses predetermined sequential workflow for novel creation",
        instruction="""You are the Novel Fix Agent - a FIXED WORKFLOW novel writing system.

SYSTEM OVERVIEW:
Unlike dynamic novel writing systems, Novel Fix uses a predetermined, sequential workflow that automatically executes in this exact order:

1. **Outline Creation** - Creates comprehensive 3-act structure
2. **Character Development** - Develops protagonist, antagonist, and supporting characters  
3. **Act 1 Writing** - Writes all setup chapters sequentially
4. **Act 2 Writing** - Writes all development chapters sequentially
5. **Act 3 Writing** - Writes all resolution chapters sequentially

KEY FEATURES:
- **Predictable**: Same workflow every time
- **Automatic**: No user guidance needed during execution
- **Sequential**: Each step builds on the previous
- **Complete**: Produces a full novel from start to finish

WORKFLOW TYPES:
- Short novel: 14 chapters (4+6+4)
- Medium novel: 20 chapters (6+8+6) 
- Long novel: 26 chapters (8+10+8)

When users want to:
- Start a new novel project → delegate to 'pipeline_controller'
- Check pipeline status → delegate to 'pipeline_controller'
- Learn about the system → explain the fixed workflow approach

Always emphasize that this is a FIXED, AUTOMATIC workflow that requires minimal user interaction once started.""",
        tools=[],
        sub_agents=[pipeline_controller],
        output_key="novel_fix_result"
    )
    
    return root_agent

# ===== STANDALONE PIPELINE EXECUTION (for testing) =====

async def create_and_run_novel(genre: str, theme: str, target_length: str = "medium"):
    """
    Creates and runs the complete novel writing pipeline.
    This function executes the entire workflow automatically.
    """
    print(f"🚀 Starting Fixed Novel Writing Pipeline")
    print(f"📚 Genre: {genre}")
    print(f"🎯 Theme: {theme}")
    print(f"📏 Target Length: {target_length}")
    print("=" * 50)
    
    # Create the pipeline agent
    pipeline_agent = create_novel_pipeline_agent(genre, theme, target_length)
    
    # Create session
    APP_NAME = "novel_fix_pipeline"
    USER_ID = "writer"
    SESSION_ID = "novel_session"
    
    # Setup session service
    session_service = InMemorySessionService()
    runner = Runner(
        app_name=APP_NAME,
        agent=pipeline_agent,
        session_service=session_service
    )
    
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    # Start the pipeline with initial prompt
    start_prompt = f"Write a {target_length} {genre} novel about {theme}. Follow the complete pipeline from outline to final chapter."
    
    print("🔄 Executing Pipeline...")
    content = types.Content(role='user', parts=[types.Part(text=start_prompt)])
    
    step_count = 0
    all_events = []
    
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        all_events.append(event)
        
        # Show agent execution progress
        if event.author and "Agent" in event.author:
            step_count += 1
            print(f"\n📝 Step {step_count}: {event.author}")
            
            # Show content if available
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text
                if len(response_text) > 150:
                    print(f"   → {response_text[:150]}...")
                else:
                    print(f"   → {response_text}")
        
        # Only break on the final response from the root SequentialAgent
        if event.is_final_response() and event.author == "NovelWritingPipeline":
            if event.content and event.content.parts:
                print(f"\n✅ Pipeline Complete!")
                print(f"Final Output: {event.content.parts[0].text[:200]}...")
            break
    
    print(f"\n🎉 Novel Writing Pipeline Completed!")
    return runner, session_service

# ===== SETUP FOR ADK WEB =====

# Session setup for ADK web
session_service = InMemorySessionService()

# Create session with initial state
APP_NAME = "novel_fix"
USER_ID = "writer_1"
SESSION_ID = "novel_fix_session_001"

initial_state = {
    "pipeline_status": "not_started",
    "pipeline_genre": None,
    "pipeline_theme": None,
    "pipeline_target_length": None
}

# Create the root agent
root_agent = create_root_agent()

async def call_agent_async(query: str, runner: Runner, user_id: str, session_id: str):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"<<< Agent Response: {event.content.parts[0].text}")
            break

async def main():
    """Main function for ADK web integration and testing."""
    
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service
    )
    
    # Initialize session
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    # Example conversations for testing
    queries = [
        "What is Novel Fix and how does it work?",
        "Start a fantasy novel about friendship and courage, medium length",
        "Check the current pipeline status",
        "Start a science fiction novel about AI ethics, short length"
    ]
    
    for query in queries:
        await call_agent_async(query, runner, USER_ID, SESSION_ID)
        await asyncio.sleep(1)  # Brief pause between queries

if __name__ == "__main__":
    # For standalone testing
    print("🧪 Testing Novel Fix Root Agent")
    asyncio.run(main()) 