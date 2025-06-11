import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from typing import Optional, Dict, Any
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure ADK to use API keys directly
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

# Model constants
MODEL_NAME = "gpt-4.1-nano"  # Azure deployment name

def create_llm():
    """Creates a LiteLLM instance configured for Azure."""
    return LiteLlm(
        model=f"azure/{MODEL_NAME}",
        api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_API_VERSION")
    )

def call_llm_for_writing(prompt: str) -> str:
    """Helper function to call LLM for actual content generation."""
    try:
        # Configure Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        # Generate content
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return f"[LLM Error: Could not generate content. {str(e)}]"

# Novel Writing Tools
def create_outline(genre: str, theme: str, target_length: str, tool_context: ToolContext) -> dict:
    """Creates a novel outline based on genre, theme, and target length."""
    print(f"--- Tool: create_outline called for {genre} novel with theme: {theme} ---")
    
    # Save to state
    tool_context.state["novel_genre"] = genre
    tool_context.state["novel_theme"] = theme
    tool_context.state["novel_target_length"] = target_length
    
    # Mock outline creation (in real implementation, this would be more sophisticated)
    outline_template = {
        "fantasy": "Epic journey with magic and mythical creatures",
        "mystery": "Crime investigation with clues and suspects", 
        "romance": "Love story with obstacles and resolution",
        "sci-fi": "Future technology and space exploration",
        "thriller": "Suspenseful plot with danger and tension"
    }
    
    base_outline = outline_template.get(genre.lower(), "General narrative structure")
    
    outline = {
        "title": f"Novel outline for {genre} story",
        "theme": theme,
        "target_length": target_length,
        "structure": {
            "act1": f"Setup - Introduce protagonist and world ({base_outline})",
            "act2": f"Development - Main conflict and challenges related to {theme}",
            "act3": f"Resolution - Climax and conclusion resolving the {theme}"
        },
        "estimated_chapters": 12 if target_length == "short" else 24
    }
    
    tool_context.state["novel_outline"] = outline
    print(f"--- Tool: Created outline and saved to state ---")
    
    return {"status": "success", "outline": outline}

def create_character_profile(character_name: str, character_role: str, tool_context: ToolContext) -> dict:
    """Creates a detailed character profile."""
    print(f"--- Tool: create_character_profile called for {character_name} as {character_role} ---")
    
    # Get novel context from state
    genre = tool_context.state.get("novel_genre", "general")
    theme = tool_context.state.get("novel_theme", "adventure")
    
    profile = {
        "name": character_name,
        "role": character_role,
        "background": f"Character background tailored for {genre} genre",
        "personality": f"Personality traits that support the {theme} theme",
        "motivation": f"Drives related to the main {theme}",
        "appearance": f"Physical description fitting {genre} setting",
        "relationships": "Connections to other characters",
        "character_arc": f"Growth journey throughout the story"
    }
    
    # Save to state
    if "character_profiles" not in tool_context.state:
        tool_context.state["character_profiles"] = {}
    tool_context.state["character_profiles"][character_name] = profile
    
    print(f"--- Tool: Created character profile for {character_name} ---")
    
    return {"status": "success", "profile": profile}

def write_chapter(chapter_number: int, chapter_focus: str, tool_context: ToolContext) -> dict:
    """Writes a chapter based on outline and character profiles."""
    print(f"--- Tool: write_chapter called for chapter {chapter_number}: {chapter_focus} ---")
    
    # Get context from state
    outline = tool_context.state.get("novel_outline", {})
    characters = tool_context.state.get("character_profiles", {})
    genre = tool_context.state.get("novel_genre", "general")
    theme = tool_context.state.get("novel_theme", "adventure")
    
    # Determine which act this chapter belongs to based on outline
    estimated_chapters = outline.get("estimated_chapters", 12)
    if chapter_number <= estimated_chapters // 3:
        current_act = "act1"
        act_description = outline.get("structure", {}).get("act1", "Setup phase")
    elif chapter_number <= (estimated_chapters * 2) // 3:
        current_act = "act2" 
        act_description = outline.get("structure", {}).get("act2", "Development phase")
    else:
        current_act = "act3"
        act_description = outline.get("structure", {}).get("act3", "Resolution phase")
    
    # Build character context
    character_context = ""
    if characters:
        character_context = "\n\nCharacter Information:\n"
        for name, profile in characters.items():
            character_context += f"- {name} ({profile.get('role', 'character')}): {profile.get('personality', '')} - {profile.get('motivation', '')}\n"
    
    # Create detailed prompt for LLM
    writing_prompt = f"""Write Chapter {chapter_number} of a {genre} novel with the theme of {theme}.

CHAPTER FOCUS: {chapter_focus}

OUTLINE CONTEXT:
- This is {current_act.upper()}: {act_description}
- Novel Theme: {theme}
- Genre: {genre}

{character_context}

WRITING GUIDELINES:
- Write approximately 800-1200 words
- Follow {current_act} story structure
- Maintain {genre} genre conventions
- Advance the {theme} theme
- Include rich descriptions, dialogue, and character development
- Create engaging prose that hooks the reader

Please write the complete chapter content now:"""

    print(f"--- Tool: Generating chapter content with LLM ---")
    
    # Call LLM to generate actual chapter content
    generated_content = call_llm_for_writing(writing_prompt)
    word_count = len(generated_content.split())
    
    chapter_content = {
        "chapter_number": chapter_number,
        "title": f"Chapter {chapter_number}: {chapter_focus}",
        "content": generated_content,
        "act": current_act,
        "act_description": act_description,
        "outline_reference": outline.get("title", "Novel outline"),
        "word_count": word_count,
        "notes": f"Chapter follows {current_act} structure from outline and uses established character profiles"
    }
    
    # Save chapter to state
    if "chapters" not in tool_context.state:
        tool_context.state["chapters"] = {}
    tool_context.state["chapters"][chapter_number] = chapter_content
    
    print(f"--- Tool: Completed chapter {chapter_number} in {current_act} ({word_count} words) ---")
    
    return {"status": "success", "chapter": chapter_content}

def get_novel_progress(tool_context: ToolContext) -> dict:
    """Gets the current progress of the novel."""
    print(f"--- Tool: get_novel_progress called ---")
    
    outline = tool_context.state.get("novel_outline", {})
    characters = tool_context.state.get("character_profiles", {})
    chapters = tool_context.state.get("chapters", {})
    
    progress = {
        "outline_complete": bool(outline),
        "character_count": len(characters),
        "chapters_written": len(chapters),
        "estimated_total_chapters": outline.get("estimated_chapters", 0),
        "completion_percentage": (len(chapters) / outline.get("estimated_chapters", 1)) * 100 if outline else 0
    }
    
    return {"status": "success", "progress": progress}

# Agent definitions
def create_agents():
    """Creates and returns the novel writing agent team."""
    # Create LLM instance
    #llm = create_llm()
    llm = "gemini-2.0-flash-exp"

    # Outline Agent
    outline_agent = Agent(
        model=llm,
        name="outline_agent",
        instruction="You are the Outline Agent. Your task is to create comprehensive novel outlines using the 'create_outline' tool. "
                   "Focus on story structure, pacing, and thematic development.",
        description="Specializes in creating detailed novel outlines with proper story structure.",
        tools=[create_outline],
    )

    # Character Profile Agent  
    character_agent = Agent(
        model=llm,
        name="character_agent",
        instruction="You are the Character Profile Agent. Your task is to create detailed character profiles using the 'create_character_profile' tool. "
                   "Focus on character development, backstory, motivation, and relationships.",
        description="Specializes in creating rich, detailed character profiles and development arcs.",
        tools=[create_character_profile],
    )

    # Import and create the sophisticated chapter writing system
    from .chapter_agents import create_chapter_agents
    act_agent = create_chapter_agents()  # This contains sub-agents for different chapter types

    # Progress Tracking Agent
    progress_agent = Agent(
        model=llm,
        name="progress_agent",
        instruction="You are the Progress Tracking Agent. Your task is to monitor novel writing progress using the 'get_novel_progress' tool. "
                   "Provide updates on completion status and suggest next steps.",
        description="Tracks writing progress and provides status updates.",
        tools=[get_novel_progress],
    )

    # Root Novel Writing Agent
    root_agent = Agent(
        name="novel_write_agent",
        model=llm,
        description="Main novel writing orchestrator: Coordinates outline creation, character development, chapter writing, and progress tracking.",
        instruction="You are the Novel Writing Agent. You coordinate the entire novel writing process. "
                   "Delegate outline creation to 'outline_agent', character development to 'character_agent', "
                   "chapter writing to 'act_agent' (which has specialized sub-agents for different chapter types), "
                   "and progress tracking to 'progress_agent'. "
                   "Ensure consistency across all elements and guide the overall narrative development.",
        tools=[],  # Root agent coordinates but doesn't have direct tools
        sub_agents=[outline_agent, character_agent, act_agent, progress_agent],
        output_key="novel_project_status"
    )

    return root_agent

async def call_agent_async(query: str, runner: Runner, user_id: str, session_id: str):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"<<< Agent Response: {event.content.parts[0].text}")
            break

# Session setup
session_service = InMemorySessionService()

# Create session with initial state
APP_NAME = "novel_writer"
USER_ID = "writer_1"
SESSION_ID = "novel_session_001"

initial_state = {
    "novel_genre": None,
    "novel_theme": None,
    "novel_target_length": None,
    "novel_outline": {},
    "character_profiles": {},
    "chapters": {}
}
root_agent = create_agents()
async def main():
    """Main function to run the novel writing agent."""

    runner = Runner(root_agent, session_service=session_service)
    
    # Initialize session
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        initial_state=initial_state
    )
    
    # Example conversations
    queries = [
        "Help me start writing a fantasy novel about friendship and loyalty, target length should be medium",
        "Create character profiles for the main protagonist and antagonist",
        "Write the first chapter introducing the main character", 
        "What's my current progress on the novel?"
    ]
    
    for query in queries:
        await call_agent_async(query, runner, USER_ID, SESSION_ID)
        await asyncio.sleep(1)  # Brief pause between queries

if __name__ == "__main__":
    asyncio.run(main()) 