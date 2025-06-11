import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any

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

# Specialized Chapter Writing Tools
def write_opening_chapter(scene_setting: str, main_character: str, hook_type: str, tool_context: ToolContext) -> dict:
    """Writes an opening chapter with strong hook and character introduction."""
    print(f"--- Tool: write_opening_chapter called for {main_character} in {scene_setting} ---")
    
    # Get context from state
    genre = tool_context.state.get("novel_genre", "general")
    theme = tool_context.state.get("novel_theme", "adventure")
    
    chapter_content = {
        "chapter_type": "opening",
        "scene_setting": scene_setting,
        "main_character": main_character,
        "hook_type": hook_type,
        "content": f"Opening chapter set in {scene_setting}, introducing {main_character}. "
                  f"Uses {hook_type} hook in {genre} style, establishing {theme} theme.",
        "writing_notes": [
            "Strong opening hook to grab reader attention",
            "Character introduction with clear motivation",
            "World-building appropriate to genre",
            "Foreshadowing of main conflict"
        ]
    }
    
    return {"status": "success", "chapter": chapter_content}

def write_action_chapter(action_type: str, conflict_level: str, characters_involved: str, tool_context: ToolContext) -> dict:
    """Writes an action-packed chapter with conflict and tension."""
    print(f"--- Tool: write_action_chapter called - {action_type} with {conflict_level} conflict ---")
    
    genre = tool_context.state.get("novel_genre", "general")
    
    chapter_content = {
        "chapter_type": "action",
        "action_type": action_type,
        "conflict_level": conflict_level,
        "characters_involved": characters_involved,
        "content": f"Action chapter featuring {action_type} with {conflict_level} intensity. "
                  f"Characters involved: {characters_involved}. Written in {genre} style.",
        "writing_notes": [
            "Fast-paced narrative with short sentences",
            "Clear action sequences easy to follow",
            "Character reactions and emotions during conflict",
            "Advancement of main plot through action"
        ]
    }
    
    return {"status": "success", "chapter": chapter_content}

def write_dialogue_chapter(conversation_purpose: str, character_dynamics: str, revelation_type: str, tool_context: ToolContext) -> dict:
    """Writes a dialogue-heavy chapter focused on character interaction."""
    print(f"--- Tool: write_dialogue_chapter called - {conversation_purpose} between {character_dynamics} ---")
    
    chapter_content = {
        "chapter_type": "dialogue",
        "conversation_purpose": conversation_purpose,
        "character_dynamics": character_dynamics,
        "revelation_type": revelation_type,
        "content": f"Dialogue-focused chapter for {conversation_purpose}. "
                  f"Character dynamics: {character_dynamics}. Reveals: {revelation_type}.",
        "writing_notes": [
            "Distinct voice for each character",
            "Natural conversation flow",
            "Subtext and character motivation",
            "Information revelation through dialogue"
        ]
    }
    
    return {"status": "success", "chapter": chapter_content}

def write_climax_chapter(climax_type: str, resolution_approach: str, emotional_peak: str, tool_context: ToolContext) -> dict:
    """Writes the climactic chapter with maximum tension and resolution."""
    print(f"--- Tool: write_climax_chapter called - {climax_type} climax with {emotional_peak} ---")
    
    theme = tool_context.state.get("novel_theme", "adventure")
    
    chapter_content = {
        "chapter_type": "climax",
        "climax_type": climax_type,
        "resolution_approach": resolution_approach,
        "emotional_peak": emotional_peak,
        "content": f"Climactic chapter with {climax_type} confrontation. "
                  f"Resolves through {resolution_approach}, reaching {emotional_peak}. "
                  f"Addresses core {theme} theme.",
        "writing_notes": [
            "Maximum tension and stakes",
            "Character growth culmination", 
            "Theme resolution",
            "Satisfying conflict resolution"
        ]
    }
    
    return {"status": "success", "chapter": chapter_content}

def create_chapter_agents():
    """Creates specialized chapter writing sub-agents."""
    llm = create_llm()
    
    # Opening Chapter Agent
    opening_agent = Agent(
        model=llm,
        name="opening_chapter_agent",
        instruction="You are the Opening Chapter Specialist. Write compelling opening chapters using 'write_opening_chapter'. "
                   "Focus on strong hooks, character introduction, and world establishment.",
        description="Specializes in writing engaging opening chapters that hook readers.",
        tools=[write_opening_chapter],
    )
    
    # Action Chapter Agent
    action_agent = Agent(
        model=llm,
        name="action_chapter_agent",
        instruction="You are the Action Chapter Specialist. Write exciting action sequences using 'write_action_chapter'. "
                   "Focus on pacing, tension, and clear action descriptions.",
        description="Specializes in writing fast-paced action and conflict chapters.",
        tools=[write_action_chapter],
    )
    
    # Dialogue Chapter Agent  
    dialogue_agent = Agent(
        model=llm,
        name="dialogue_chapter_agent",
        instruction="You are the Dialogue Chapter Specialist. Write character-driven dialogue chapters using 'write_dialogue_chapter'. "
                   "Focus on character voice, relationship dynamics, and information revelation.",
        description="Specializes in writing dialogue-heavy chapters with strong character interaction.",
        tools=[write_dialogue_chapter],
    )
    
    # Climax Chapter Agent
    climax_agent = Agent(
        model=llm,
        name="climax_chapter_agent", 
        instruction="You are the Climax Chapter Specialist. Write powerful climactic chapters using 'write_climax_chapter'. "
                   "Focus on maximum tension, character resolution, and thematic payoff.",
        description="Specializes in writing climactic chapters with emotional and plot resolution.",
        tools=[write_climax_chapter],
    )
    
    # Master Chapter Writing Agent (coordinates the sub-agents)
    master_chapter_agent = Agent(
        name="act_agent",
        model=llm,
        description="Act Writing Coordinator: Manages different types of chapter writing through specialized sub-agents.",
        instruction="You are the Act Agent, coordinating chapter writing across different chapter types. "
                   "Delegate opening chapters to 'opening_chapter_agent', action scenes to 'action_chapter_agent', "
                   "dialogue scenes to 'dialogue_chapter_agent', and climactic scenes to 'climax_chapter_agent'. "
                   "Ensure each chapter type is handled by the appropriate specialist.",
        tools=[],  # Coordinates through sub-agents
        sub_agents=[opening_agent, action_agent, dialogue_agent, climax_agent],
        output_key="chapter_writing_result"
    )
    
    return master_chapter_agent

# Example usage function
def get_chapter_writing_system():
    """Returns the complete chapter writing system."""
    return create_chapter_agents() 