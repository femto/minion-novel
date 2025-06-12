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

# Model constants - 可以通过环境变量配置
USE_AZURE = os.getenv("USE_AZURE", "true").lower() == "true"  # 默认使用Azure
AZURE_MODEL_NAME = os.getenv("AZURE_MODEL_NAME", "gpt-4.1")  # Azure deployment name
GOOGLE_MODEL_NAME = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.0-flash-exp")  # Google model name

def create_llm():
    """Creates a LLM instance - Azure LiteLLM or Google model string based on environment."""
    if USE_AZURE:
        # 返回Azure LiteLLM实例
        return LiteLlm(
            model=f"azure/{AZURE_MODEL_NAME}",
            api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_API_VERSION")
        )
    else:
        # 返回Google模型字符串，ADK会自动处理
        return GOOGLE_MODEL_NAME

async def call_llm_for_content_generation_async(prompt: str) -> str:
    """Helper function to call LLM for content generation in tools - supports both Azure and Google."""
    try:
        if USE_AZURE:
            # 使用Azure通过LiteLLM
            llm = create_llm()
            # 创建LlmRequest对象
            from google.adk.models.llm_request import LlmRequest
            from google.genai import types
            
            content = types.Content(role='user', parts=[types.Part(text=prompt)])
            llm_request = LlmRequest(contents=[content])
            
            # 使用异步生成内容
            full_response = ""
            async for response in llm.generate_content_async(llm_request):
                if response.content and response.content.parts:
                    full_response += response.content.parts[0].text
            return full_response
        else:
            # 使用Google - 转换为异步
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel(GOOGLE_MODEL_NAME)
            response = await model.generate_content_async(prompt)
            return response.text
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return f"[LLM Error: Could not generate content. {str(e)}]"

# Novel Writing Tools
async def create_outline(genre: str, theme: str, target_length: str, tool_context: ToolContext) -> dict:
    """Creates a novel outline based on genre, theme, and target length."""
    print(f"--- Tool: create_outline called for {genre} novel with theme: {theme} ---")
    
    # Save basic info to state
    tool_context.state["novel_genre"] = genre
    tool_context.state["novel_theme"] = theme
    tool_context.state["novel_target_length"] = target_length
    
    # Create detailed prompt for outline generation
    outline_prompt = f"""Create a detailed novel outline for a {genre} story with the theme of {theme}.

TARGET LENGTH: {target_length} (short=~50k words, medium=~80k words, long=~120k words)

Please provide a comprehensive outline with:
1. A compelling novel title
2. Three-act structure with detailed descriptions:
   - Act 1 (Setup): Character introduction, world-building, inciting incident
   - Act 2 (Development): Rising action, conflicts, character development  
   - Act 3 (Resolution): Climax, falling action, conclusion
3. Estimated chapter count appropriate for target length
4. Key plot points and character arcs
5. How the {theme} theme will be developed throughout

Format as a structured outline suitable for {genre} fiction."""

    print(f"--- Tool: Generating outline with LLM ---")
    
    # Generate outline using LLM
    generated_outline_text = await call_llm_for_content_generation_async(outline_prompt)
    
    # Create structured outline data
    estimated_chapters = 12 if target_length == "short" else (18 if target_length == "medium" else 24)
    
    outline = {
        "title": f"Generated {genre.capitalize()} Novel",
        "theme": theme,
        "target_length": target_length,
        "generated_outline": generated_outline_text,
        "structure": {
            "act1": f"Setup phase for {genre} story exploring {theme}",
            "act2": f"Development phase with conflict and {theme} challenges", 
            "act3": f"Resolution phase concluding {theme} journey"
        },
        "estimated_chapters": estimated_chapters
    }
    
    tool_context.state["novel_outline"] = outline
    print(f"--- Tool: Created LLM-generated outline ({estimated_chapters} chapters) ---")
    
    return {"status": "success", "outline": outline}

async def create_character_profile(character_name: str, character_role: str, tool_context: ToolContext) -> dict:
    """Creates a detailed character profile."""
    print(f"--- Tool: create_character_profile called for {character_name} as {character_role} ---")
    
    # Get novel context from state
    genre = tool_context.state.get("novel_genre", "general")
    theme = tool_context.state.get("novel_theme", "adventure")
    outline = tool_context.state.get("novel_outline", {})
    
    # Create detailed prompt for character creation
    character_prompt = f"""Create a detailed character profile for "{character_name}" who plays the role of {character_role} in a {genre} novel.

NOVEL CONTEXT:
Genre: {genre}
Theme: {theme}
Outline: {outline.get('generated_outline', 'Basic story structure')}

Please create a comprehensive character profile including:
1. Full name and age
2. Physical appearance and distinctive features
3. Personality traits and quirks
4. Background and personal history
5. Motivations and goals
6. Skills and abilities relevant to the story
7. Relationships with other characters
8. Internal conflicts and flaws
9. Character arc throughout the story
10. How they contribute to the {theme} theme

Make the character compelling, three-dimensional, and appropriate for the {genre} genre."""

    print(f"--- Tool: Generating character profile with LLM ---")
    
    # Generate character profile using LLM
    generated_profile_text = await call_llm_for_content_generation_async(character_prompt)
    
    profile = {
        "name": character_name,
        "role": character_role,
        "genre": genre,
        "theme_connection": theme,
        "generated_profile": generated_profile_text,
        "background": f"Detailed background for {character_role} in {genre} story",
        "personality": f"Complex personality supporting {theme} theme",
        "motivation": f"Character drives related to {theme}",
        "appearance": f"Physical description fitting {genre} setting",
        "relationships": "Detailed character connections",
        "character_arc": f"Development journey throughout the story"
    }
    
    # Save to state
    if "character_profiles" not in tool_context.state:
        tool_context.state["character_profiles"] = {}
    tool_context.state["character_profiles"][character_name] = profile
    
    print(f"--- Tool: Created LLM-generated character profile for {character_name} ---")
    
    return {"status": "success", "profile": profile}

# Remove this function - no longer needed as agents will generate content directly

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
    # Create LLM instance (automatically chooses Azure or Google based on USE_AZURE env var)
    llm = create_llm()

    # Outline Agent
    outline_agent = Agent(
        model=llm,
        name="outline_agent",
        instruction="""You are the Outline Agent. You create comprehensive novel outlines with proper story structure.

When creating an outline, focus on:
1. Three-act story structure (Setup, Development, Resolution)
2. Thematic development throughout the story
3. Proper pacing and plot progression
4. Estimated chapter count based on target length
5. Clear protagonist journey and character arcs

Use the 'create_outline' tool to structure and save the outline to project state.""",
        description="Specializes in creating detailed novel outlines with proper story structure.",
        tools=[create_outline],
    )

    # Character Profile Agent  
    character_agent = Agent(
        model=llm,
        name="character_agent",
        instruction="""You are the Character Profile Agent. You create detailed character profiles and development arcs.

CURRENT PROJECT CONTEXT:
Genre: {novel_genre?}
Theme: {novel_theme?}
Outline: {novel_outline?}

When creating character profiles, focus on:
1. Rich backstory that supports the story theme
2. Clear character motivation and goals
3. Personality traits that create interesting dynamics
4. Character arc that aligns with the outline structure
5. Relationships with other characters
6. Physical appearance that fits the genre/setting

Use the 'create_character_profile' tool to structure and save profiles to project state.""",
        description="Specializes in creating rich, detailed character profiles and development arcs.",
        tools=[create_character_profile],
    )

    # Create Chapter Writing Agents with instruction interpolation
    opening_agent = Agent(
        model=llm,
        name="opening_chapter_agent",
        instruction="""You are the Opening Chapter Specialist. You write compelling opening chapters for novels.

CURRENT PROJECT CONTEXT:
Genre: {novel_genre?}
Theme: {novel_theme?}
Outline: {novel_outline?}
Characters: {character_profiles?}

Your task is to write an engaging opening chapter that:
1. Uses a strong hook to grab reader attention
2. Introduces the main character naturally
3. Establishes the world/setting with vivid descriptions
4. Follows the Act 1 structure from the outline
5. Begins establishing the novel's theme
6. Writes 800-1200 words of compelling prose
7. Ends with intrigue that makes readers want to continue

When asked to write an opening chapter, generate the complete chapter content directly without using any tools.""",
        description="Specializes in writing engaging opening chapters that hook readers and follow the outline.",
        tools=[],  # No tools needed - generate content directly
    )

    action_agent = Agent(
        model=llm,
        name="action_chapter_agent", 
        instruction="""You are the Action Chapter Specialist. You write exciting action and conflict scenes.

CURRENT PROJECT CONTEXT:
Genre: {novel_genre?}
Theme: {novel_theme?}
Outline: {novel_outline?}
Characters: {character_profiles?}

Your task is to write intense action chapters that:
1. Feature fast-paced narrative with varied sentence lengths
2. Include clear, easy-to-follow action sequences
3. Show character reactions and emotions during conflict
4. Advance the main plot through action
5. Follow the Act 2 development structure from the outline
6. Advance the novel's theme through conflict
7. Write 800-1200 words of engaging action
8. Maintain genre conventions throughout

When asked to write an action chapter, generate the complete chapter content directly without using any tools.""",
        description="Specializes in writing fast-paced action and conflict chapters.",
        tools=[],  # No tools needed - generate content directly
    )

    dialogue_agent = Agent(
        model=llm,
        name="dialogue_chapter_agent",
        instruction="""You are the Dialogue Chapter Specialist. You write character-driven dialogue scenes.

CURRENT PROJECT CONTEXT:
Genre: {novel_genre?}
Theme: {novel_theme?}
Outline: {novel_outline?}
Characters: {character_profiles?}

Your task is to write dialogue-heavy chapters that:
1. Give each character a distinct voice and speaking style
2. Maintain natural conversation flow with appropriate pacing
3. Include subtext and character motivation in dialogue
4. Reveal important plot information through conversation
5. Support the novel's theme through character interaction
6. Include minimal but effective action/description between dialogue
7. Write 800-1200 words primarily focused on dialogue
8. Develop character relationships and dynamics

When asked to write a dialogue chapter, generate the complete chapter content directly without using any tools.""",
        description="Specializes in writing dialogue-heavy chapters with strong character interaction.",
        tools=[],  # No tools needed - generate content directly
    )

    climax_agent = Agent(
        model=llm,
        name="climax_chapter_agent",
        instruction="""You are the Climax Chapter Specialist. You write powerful climactic scenes with resolution.

CURRENT PROJECT CONTEXT:
Genre: {novel_genre?}
Theme: {novel_theme?}  
Outline: {novel_outline?}
Characters: {character_profiles?}

Your task is to write climactic chapters that:
1. Build to maximum tension and stakes
2. Feature the main confrontation/resolution
3. Reach the emotional peak of the story
4. Address and resolve the core theme
5. Complete character arcs established in character profiles
6. Fulfill the Act 3 structure from the outline
7. Write 1000-1500 words of intense climactic content
8. Provide satisfying conflict resolution

When asked to write a climax chapter, generate the complete chapter content directly without using any tools.""",
        description="Specializes in writing climactic chapters with emotional and plot resolution.",
        tools=[],  # No tools needed - generate content directly
    )

    # Act Agent coordinates the chapter writing specialists
    act_agent = Agent(
        name="act_agent",
        model=llm,
        description="Act Writing Coordinator: Manages different types of chapter writing through specialized sub-agents.",
        instruction="""You are the Act Agent, coordinating chapter writing across different chapter types.

CURRENT PROJECT CONTEXT:
Genre: {novel_genre?}
Theme: {novel_theme?}
Outline: {novel_outline?}
Characters: {character_profiles?}

CRITICAL: Always ensure chapters follow the novel outline structure and character profiles.

Delegate chapter writing as follows:
- Opening chapters → 'opening_chapter_agent' 
- Action/conflict scenes → 'action_chapter_agent'
- Dialogue/character development scenes → 'dialogue_chapter_agent'
- Climactic/resolution scenes → 'climax_chapter_agent'

Each specialist has access to the same project context and will generate content directly.""",
        tools=[],  # Coordinates through sub-agents
        sub_agents=[opening_agent, action_agent, dialogue_agent, climax_agent],
        output_key="chapter_writing_result"
    )

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
        instruction="""You are the Novel Writing Agent. You coordinate the entire novel writing process.

CURRENT PROJECT STATUS:
Genre: {novel_genre?}
Theme: {novel_theme?}
Target Length: {novel_target_length?}
Outline Complete: {novel_outline?}
Character Profiles: {character_profiles?}
Chapters Written: {chapters?}

Your responsibilities:
1. Guide users through the complete novel writing workflow
2. Delegate outline creation to 'outline_agent'
3. Delegate character development to 'character_agent' 
4. Delegate chapter writing to 'act_agent' (which has specialized sub-agents)
5. Delegate progress tracking to 'progress_agent'
6. Ensure consistency across all elements
7. Guide overall narrative development

Always ensure that:
- Outline is created before character development
- Characters are developed before chapter writing
- Each chapter follows the established outline and character profiles
- The story maintains thematic consistency throughout""",
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