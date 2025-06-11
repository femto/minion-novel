import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any
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

# Specialized Chapter Writing Tools
def write_opening_chapter(scene_setting: str, main_character: str, hook_type: str, tool_context: ToolContext) -> dict:
    """Writes an opening chapter with strong hook and character introduction."""
    print(f"--- Tool: write_opening_chapter called for {main_character} in {scene_setting} ---")
    
    # Get context from state
    genre = tool_context.state.get("novel_genre", "general")
    theme = tool_context.state.get("novel_theme", "adventure")
    outline = tool_context.state.get("novel_outline", {})
    characters = tool_context.state.get("character_profiles", {})
    
    # Reference outline Act 1 structure
    act1_structure = outline.get("structure", {}).get("act1", "Setup phase")
    character_info = characters.get(main_character, {})
    
    # Build character context
    character_context = ""
    if character_info:
        character_context = f"""
CHARACTER PROFILE - {main_character}:
- Role: {character_info.get('role', 'protagonist')}
- Background: {character_info.get('background', 'to be developed')}
- Personality: {character_info.get('personality', 'to be developed')}
- Motivation: {character_info.get('motivation', 'to be developed')}
- Appearance: {character_info.get('appearance', 'to be described')}
"""
    
    # Create detailed prompt for opening chapter
    writing_prompt = f"""Write the opening chapter of a {genre} novel with the theme of {theme}.

CHAPTER REQUIREMENTS:
- Setting: {scene_setting}
- Main Character: {main_character}
- Hook Type: {hook_type}
- Act 1 Structure: {act1_structure}

{character_context}

WRITING GUIDELINES:
- Start with a compelling {hook_type} hook
- Introduce {main_character} naturally in the scene
- Establish the {scene_setting} with vivid descriptions
- Follow {genre} genre conventions
- Begin establishing the {theme} theme
- Write 800-1200 words
- Use engaging prose with good pacing
- End with intrigue that makes readers want to continue

Please write the complete opening chapter now:"""

    print(f"--- Tool: Generating opening chapter content with LLM ---")
    
    # Call LLM to generate actual chapter content
    generated_content = call_llm_for_writing(writing_prompt)
    word_count = len(generated_content.split())
    
    chapter_content = {
        "chapter_type": "opening",
        "scene_setting": scene_setting,
        "main_character": main_character,
        "hook_type": hook_type,
        "content": generated_content,
        "outline_alignment": act1_structure,
        "character_reference": character_info.get("name", main_character),
        "word_count": word_count,
        "writing_notes": [
            "Strong opening hook to grab reader attention",
            "Character introduction with clear motivation",
            "World-building appropriate to genre", 
            "Foreshadowing of main conflict",
            f"Aligns with outline Act 1: {act1_structure}"
        ]
    }
    
    print(f"--- Tool: Completed opening chapter ({word_count} words) ---")
    
    return {"status": "success", "chapter": chapter_content}

def write_action_chapter(action_type: str, conflict_level: str, characters_involved: str, tool_context: ToolContext) -> dict:
    """Writes an action-packed chapter with conflict and tension."""
    print(f"--- Tool: write_action_chapter called - {action_type} with {conflict_level} conflict ---")
    
    # Get context from state
    genre = tool_context.state.get("novel_genre", "general")
    theme = tool_context.state.get("novel_theme", "adventure")
    outline = tool_context.state.get("novel_outline", {})
    characters = tool_context.state.get("character_profiles", {})
    
    # Usually action chapters are in Act 2 (development/conflict)
    act2_structure = outline.get("structure", {}).get("act2", "Development and conflict phase")
    
    # Create writing prompt for action chapter
    writing_prompt = f"""Write an action chapter for a {genre} novel with the theme of {theme}.

ACTION REQUIREMENTS:
- Action Type: {action_type}
- Conflict Level: {conflict_level}
- Characters Involved: {characters_involved}
- Act 2 Structure: {act2_structure}

WRITING GUIDELINES:
- Write 800-1200 words of intense {action_type}
- Maintain {conflict_level} intensity throughout
- Include all specified characters: {characters_involved}
- Use fast-paced narrative with varied sentence lengths
- Show clear action sequences that are easy to follow
- Include character reactions and emotions during conflict
- Advance the {theme} theme through the action
- Follow {genre} genre conventions

Please write the complete action chapter now:"""

    print(f"--- Tool: Generating action chapter content with LLM ---")
    
    # Call LLM to generate actual chapter content
    generated_content = call_llm_for_writing(writing_prompt)
    word_count = len(generated_content.split())

    chapter_content = {
        "chapter_type": "action",
        "action_type": action_type,
        "conflict_level": conflict_level,
        "characters_involved": characters_involved,
        "content": generated_content,
        "outline_alignment": act2_structure,
        "theme_advancement": theme,
        "word_count": word_count,
        "writing_notes": [
            "Fast-paced narrative with short sentences",
            "Clear action sequences easy to follow",
            "Character reactions and emotions during conflict",
            "Advancement of main plot through action",
            f"Develops conflict as outlined in: {act2_structure}"
        ]
    }
    
    print(f"--- Tool: Completed action chapter ({word_count} words) ---")
    
    return {"status": "success", "chapter": chapter_content}

def write_dialogue_chapter(conversation_purpose: str, character_dynamics: str, revelation_type: str, tool_context: ToolContext) -> dict:
    """Writes a dialogue-heavy chapter focused on character interaction."""
    print(f"--- Tool: write_dialogue_chapter called - {conversation_purpose} between {character_dynamics} ---")
    
    # Get context from state
    genre = tool_context.state.get("novel_genre", "general")
    theme = tool_context.state.get("novel_theme", "adventure")
    outline = tool_context.state.get("novel_outline", {})
    characters = tool_context.state.get("character_profiles", {})
    
    # Dialogue chapters can appear in any act, but often in Act 1 (setup) or Act 2 (development)
    act_structures = outline.get("structure", {})
    relevant_structure = f"Act 1: {act_structures.get('act1', '')} / Act 2: {act_structures.get('act2', '')}"
    
    # Create writing prompt for dialogue chapter
    writing_prompt = f"""Write a dialogue-heavy chapter for a {genre} novel with the theme of {theme}.

DIALOGUE REQUIREMENTS:
- Conversation Purpose: {conversation_purpose}
- Character Dynamics: {character_dynamics}
- Revelation Type: {revelation_type}
- Theme Development: {theme}

WRITING GUIDELINES:
- Write 800-1200 words primarily focused on dialogue
- Give each character a distinct voice and speaking style
- Maintain natural conversation flow with appropriate pacing
- Include subtext and character motivation in the dialogue
- Reveal important information: {revelation_type}
- Support the {theme} theme through character interaction
- Include minimal but effective action/description between dialogue
- Follow {genre} genre conventions

Please write the complete dialogue chapter now:"""

    print(f"--- Tool: Generating dialogue chapter content with LLM ---")
    
    # Call LLM to generate actual chapter content
    generated_content = call_llm_for_writing(writing_prompt)
    word_count = len(generated_content.split())

    chapter_content = {
        "chapter_type": "dialogue",
        "conversation_purpose": conversation_purpose,
        "character_dynamics": character_dynamics,
        "revelation_type": revelation_type,
        "content": generated_content,
        "outline_reference": relevant_structure,
        "theme_development": theme,
        "character_arcs": [char.get("character_arc", "development") for char in characters.values()],
        "word_count": word_count,
        "writing_notes": [
            "Distinct voice for each character",
            "Natural conversation flow",
            "Subtext and character motivation",
            "Information revelation through dialogue",
            f"Character development aligns with outline themes"
        ]
    }
    
    print(f"--- Tool: Completed dialogue chapter ({word_count} words) ---")
    
    return {"status": "success", "chapter": chapter_content}

def write_climax_chapter(climax_type: str, resolution_approach: str, emotional_peak: str, tool_context: ToolContext) -> dict:
    """Writes the climactic chapter with maximum tension and resolution."""
    print(f"--- Tool: write_climax_chapter called - {climax_type} climax with {emotional_peak} ---")
    
    # Get context from state
    genre = tool_context.state.get("novel_genre", "general")
    theme = tool_context.state.get("novel_theme", "adventure")
    outline = tool_context.state.get("novel_outline", {})
    characters = tool_context.state.get("character_profiles", {})
    
    # Climax chapters are in Act 3 (resolution)
    act3_structure = outline.get("structure", {}).get("act3", "Resolution and conclusion")
    character_arcs = [char.get("character_arc", "growth") for char in characters.values()]
    
    # Build character context for climax
    character_names = [char.get('name', 'character') for char in characters.values()]
    character_context = ""
    if characters:
        character_context = "\n\nCHARACTER ARCS TO COMPLETE:\n"
        for name, profile in characters.items():
            character_context += f"- {name}: {profile.get('character_arc', 'growth and resolution')}\n"

    # Create writing prompt for climax chapter
    writing_prompt = f"""Write the climactic chapter for a {genre} novel with the theme of {theme}.

CLIMAX REQUIREMENTS:
- Climax Type: {climax_type}
- Resolution Approach: {resolution_approach}
- Emotional Peak: {emotional_peak}
- Act 3 Structure: {act3_structure}

{character_context}

WRITING GUIDELINES:
- Write 1000-1500 words of intense climactic action
- Build to maximum tension and stakes
- Feature {climax_type} confrontation as the centerpiece
- Resolve through {resolution_approach}
- Reach {emotional_peak} emotional intensity
- Address and resolve the core {theme} theme
- Complete character arcs for: {', '.join(character_names)}
- Provide satisfying conflict resolution
- Deliver on the promises made in the outline
- Follow {genre} genre conventions

Please write the complete climactic chapter now:"""

    print(f"--- Tool: Generating climax chapter content with LLM ---")
    
    # Call LLM to generate actual chapter content
    generated_content = call_llm_for_writing(writing_prompt)
    word_count = len(generated_content.split())

    chapter_content = {
        "chapter_type": "climax",
        "climax_type": climax_type,
        "resolution_approach": resolution_approach,
        "emotional_peak": emotional_peak,
        "content": generated_content,
        "outline_fulfillment": act3_structure,
        "theme_resolution": theme,
        "character_arc_completion": character_arcs,
        "word_count": word_count,
        "writing_notes": [
            "Maximum tension and stakes",
            "Character growth culmination", 
            "Theme resolution",
            "Satisfying conflict resolution",
            f"Delivers on outline promise: {act3_structure}",
            "All character arcs reach resolution"
        ]
    }
    
    print(f"--- Tool: Completed climax chapter ({word_count} words) ---")
    
    return {"status": "success", "chapter": chapter_content}

def create_chapter_agents():
    """Creates specialized chapter writing sub-agents."""
    #llm = create_llm()
    llm = "gemini-2.0-flash-exp"
    
    # Opening Chapter Agent
    opening_agent = Agent(
        model=llm,
        name="opening_chapter_agent",
        instruction="You are the Opening Chapter Specialist. Write compelling opening chapters using 'write_opening_chapter'. "
                   "ALWAYS reference the novel outline Act 1 structure and character profiles from the project state. "
                   "Focus on strong hooks, character introduction, world establishment, and alignment with outline.",
        description="Specializes in writing engaging opening chapters that hook readers and follow the outline.",
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
                   "CRITICAL: Always ensure chapters follow the novel outline structure and character profiles. "
                   "Delegate opening chapters to 'opening_chapter_agent', action scenes to 'action_chapter_agent', "
                   "dialogue scenes to 'dialogue_chapter_agent', and climactic scenes to 'climax_chapter_agent'. "
                   "Ensure each chapter type is handled by the appropriate specialist and references the outline.",
        tools=[],  # Coordinates through sub-agents
        sub_agents=[opening_agent, action_agent, dialogue_agent, climax_agent],
        output_key="chapter_writing_result"
    )
    
    return master_chapter_agent

# Example usage function
def get_chapter_writing_system():
    """Returns the complete chapter writing system."""
    return create_chapter_agents() 