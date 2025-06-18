import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent, Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

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



# ===== WORKFLOW AGENTS FOR FIXED PIPELINE =====

def create_act_agent(act_name: str):
    """Creates an agent for writing a specific act of the novel."""
    llm = create_llm()
    
    act_instructions = {
        "Act 1": """You are the Act 1 Writer for the Novel Fix system.

Your job is to write all chapters for Act 1 (Setup) based on information from previous steps.

INPUT: Use information from previous agents:
- Extracted parameters (genre, theme, length)
- Novel outline (specifically Act 1 chapters)
- Character profiles

ACT 1 FOCUS:
- Introduce protagonist and world
- Establish the main conflict/problem
- Hook the reader with engaging opening
- Set up character relationships
- End with inciting incident

CHAPTER COUNT (based on length):
- Short novel: 4 chapters
- Medium novel: 6 chapters  
- Long novel: 8 chapters

OUTPUT: Write each chapter in sequence:
- Chapter title
- Full chapter content (2000-3000 words per chapter)
- Smooth transitions between chapters
- Consistent character voice and style""",

        "Act 2": """You are the Act 2 Writer for the Novel Fix system.

Your job is to write all chapters for Act 2 (Development) based on information from previous steps.

INPUT: Use information from previous agents:
- Extracted parameters, outline, characters
- Act 1 content for continuity

ACT 2 FOCUS:
- Develop main conflict and obstacles
- Character growth and relationship development
- Rising action and complications
- Midpoint crisis or revelation
- Build toward climax

CHAPTER COUNT (based on length):
- Short novel: 6 chapters
- Medium novel: 8 chapters
- Long novel: 10 chapters

OUTPUT: Write each chapter in sequence:
- Chapter title
- Full chapter content (2000-3000 words per chapter)
- Continue story from Act 1
- Build tension toward Act 3""",

        "Act 3": """You are the Act 3 Writer for the Novel Fix system.

Your job is to write all chapters for Act 3 (Resolution) based on information from previous steps.

INPUT: Use information from previous agents:
- Extracted parameters, outline, characters
- Act 1 and Act 2 content for continuity

ACT 3 FOCUS:
- Climax and confrontation
- Resolution of main conflict
- Character arc completion
- Tie up subplots and loose ends
- Satisfying conclusion

CHAPTER COUNT (based on length):
- Short novel: 4 chapters
- Medium novel: 6 chapters
- Long novel: 8 chapters

OUTPUT: Write each chapter in sequence:
- Chapter title
- Full chapter content (2000-3000 words per chapter)
- Continue story from Acts 1 & 2
- Provide satisfying conclusion"""
    }
    
    return Agent(
        model=llm,
        name=f"{act_name.lower().replace(' ', '_')}_writer",
        instruction=act_instructions[act_name],
        description=f"Writes all chapters for {act_name} based on outline and character profiles",
        output_key=f"{act_name.lower().replace(' ', '_')}_content"
    )

# ===== PARAMETER EXTRACTION =====

def extract_novel_params_from_text(user_input: str) -> dict:
    """Extract genre, theme, and target_length from user input text."""
    import re
    
    # Default values
    params = {
        "genre": "fantasy",
        "theme": "adventure and discovery", 
        "target_length": "medium"
    }
    
    # Extract genre
    genre_patterns = [
        r"(fantasy|science fiction|sci-fi|mystery|romance|thriller|horror|historical|adventure|drama)",
        r"write.*?(fantasy|science fiction|sci-fi|mystery|romance|thriller|horror|historical|adventure|drama)",
        r"(fantasy|science fiction|sci-fi|mystery|romance|thriller|horror|historical|adventure|drama).*?novel"
    ]
    
    for pattern in genre_patterns:
        match = re.search(pattern, user_input.lower())
        if match:
            genre = match.group(1)
            if genre == "sci-fi":
                genre = "science fiction"
            params["genre"] = genre
            break
    
    # Extract target length
    length_patterns = [
        r"(short|medium|long).*?length",
        r"(short|medium|long).*?novel",
        r"length.*?(short|medium|long)",
        r"write.*?(short|medium|long)"
    ]
    
    for pattern in length_patterns:
        match = re.search(pattern, user_input.lower())
        if match:
            params["target_length"] = match.group(1)
            break
    
    # Extract theme (more complex, look for "about X" patterns)
    theme_patterns = [
        r"about\s+([^,\.!?]+)",
        r"theme.*?[:\-]\s*([^,\.!?]+)",
        r"story.*?about\s+([^,\.!?]+)"
    ]
    
    for pattern in theme_patterns:
        match = re.search(pattern, user_input.lower())
        if match:
            theme = match.group(1).strip()
            if len(theme) > 5:  # Only use if it's substantial
                params["theme"] = theme
            break
    
    return params



# ===== PARAMETER EXTRACTION AGENT =====

def create_parameter_extraction_agent():
    """Creates an agent that extracts genre, theme, and target_length from user input."""
    llm = create_llm()
    
    return Agent(
        model=llm,
        name="parameter_extractor",
        instruction="""You are a Parameter Extraction Agent for the Novel Fix system.

Your job is to extract three key parameters from user input:
1. **Genre**: fantasy, science fiction, mystery, romance, thriller, horror, historical, adventure, drama
2. **Theme**: What the story is about (extract from patterns like "about X", "story of X")
3. **Target Length**: short, medium, or long

EXTRACTION RULES:
- Look for explicit mentions of genre, theme, and length
- Use smart defaults if not specified:
  - Default genre: "fantasy"
  - Default theme: "adventure and discovery" 
  - Default length: "medium"

OUTPUT FORMAT:
Always respond with exactly this format:
Genre: [extracted_genre]
Theme: [extracted_theme]  
Length: [extracted_length]

Examples:
Input: "Write a mystery novel about a detective in a small town"
Output: 
Genre: mystery
Theme: a detective in a small town
Length: medium

Input: "I want a short science fiction story about space exploration"
Output:
Genre: science fiction
Theme: space exploration
Length: short""",
        description="Extracts novel parameters from user input",
        output_key="extracted_parameters"
    )

def create_outline_agent():
    """Creates the agent responsible for creating the novel outline."""
    llm = create_llm()
    
    return Agent(
        model=llm,
        name="outline_creator",
        instruction="""You are the Outline Creator for the Novel Fix system.

Your job is to create a comprehensive 3-act novel outline based on the extracted parameters from the previous step.

INPUT: Read the extracted parameters from the previous agent:
- Genre: The story genre
- Theme: What the story is about  
- Length: Determines chapter count (short=14, medium=20, long=26 chapters)

CHAPTER DISTRIBUTION:
- Short (14 chapters): Act 1 (4 chapters), Act 2 (6 chapters), Act 3 (4 chapters)
- Medium (20 chapters): Act 1 (6 chapters), Act 2 (8 chapters), Act 3 (6 chapters)  
- Long (26 chapters): Act 1 (8 chapters), Act 2 (10 chapters), Act 3 (8 chapters)

OUTPUT: Create a detailed outline with:
1. **Story Summary**: One paragraph overview
2. **Act 1 Outline**: Chapter-by-chapter breakdown for setup
3. **Act 2 Outline**: Chapter-by-chapter breakdown for development
4. **Act 3 Outline**: Chapter-by-chapter breakdown for resolution

Each chapter should have:
- Chapter title
- 2-3 sentence summary of events
- Key plot points or character developments

Make sure the outline fits the specified genre and theme.""",
        description="Creates detailed 3-act novel outline based on extracted parameters",
        output_key="novel_outline"
    )

def create_character_agent():
    """Creates the agent responsible for character development."""
    llm = create_llm()
    
    return Agent(
        model=llm,
        name="character_developer",
        instruction="""You are the Character Developer for the Novel Fix system.

Your job is to create detailed character profiles based on the outline and parameters.

INPUT: Use information from previous steps:
- Extracted parameters (genre, theme, length)
- Novel outline with plot structure

OUTPUT: Create character profiles for:

1. **PROTAGONIST**:
   - Name and age
   - Background and motivation
   - Character arc throughout the story
   - Key personality traits
   - Strengths and flaws

2. **ANTAGONIST** (if applicable to genre):
   - Name and background
   - Opposing goals to protagonist
   - Methods and motivation
   - Connection to main conflict

3. **SUPPORTING CHARACTERS** (2-3 key characters):
   - Names and roles in story
   - Relationship to protagonist
   - How they help/hinder the plot

4. **CHARACTER RELATIONSHIPS**:
   - How characters interact
   - Key relationship dynamics
   - How relationships evolve

Ensure characters fit the genre and support the theme effectively.""",
        description="Develops protagonist, antagonist, and supporting characters",
        output_key="character_profiles"
    )

# ===== SIMPLIFIED ROOT AGENT =====

def create_root_agent():
    """Creates the root agent as a SequentialAgent with parameter extraction and writing steps."""
    
    # Create all sub-agents
    parameter_agent = create_parameter_extraction_agent()
    outline_agent = create_outline_agent()
    character_agent = create_character_agent()
    act1_agent = create_act_agent("Act 1")
    act2_agent = create_act_agent("Act 2") 
    act3_agent = create_act_agent("Act 3")
    
    # Create the sequential workflow
    root_agent = SequentialAgent(
        name="novel_fix_sequential_pipeline",
        description="Complete novel writing pipeline: parameter extraction → outline → characters → Act 1 → Act 2 → Act 3",
        sub_agents=[
            parameter_agent,
            outline_agent,
            character_agent,
            act1_agent,
            act2_agent,
            act3_agent
        ]
    )
    
    return root_agent

# ===== STANDALONE PIPELINE EXECUTION (for testing) =====

async def create_and_run_novel(genre: str, theme: str, target_length: str):
    """Standalone function to create and run the complete novel pipeline."""
    print(f"🚀 Starting Novel Fix Pipeline")
    print(f"📖 Genre: {genre}")
    print(f"🎯 Theme: {theme}")
    print(f"📏 Length: {target_length}")
    print("=" * 50)
    
    # Create the root agent (which is now a SequentialAgent)
    root_agent = create_root_agent()
    
    # Run the pipeline (in a real implementation, you'd use a Runner)
    print("✨ Root agent created successfully!")
    print("🎬 Ready to execute the complete novel writing workflow!")
    
    return root_agent

# ===== SETUP FOR ADK WEB =====

# Constants for web service
APP_NAME = "novel_fix"
USER_ID = "writer_1"
SESSION_ID = "novel_fix_session_001"

async def call_agent_async(query: str, runner: Runner, user_id: str, session_id: str):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"<<< Agent Response: {event.content.parts[0].text}")
            break

root_agent = create_root_agent()

async def main():
    """Main function for ADK web integration and testing."""
    
    # Create session service and root agent
    session_service = InMemorySessionService()

    
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

def get_chapter_counts(target_length: str) -> dict:
    """Returns chapter count breakdown for each act based on target length."""
    chapter_counts = {
        "short": {"act1": 4, "act2": 6, "act3": 4, "total": 14},
        "medium": {"act1": 6, "act2": 8, "act3": 6, "total": 20},
        "long": {"act1": 8, "act2": 10, "act3": 8, "total": 26}
    }
    return chapter_counts.get(target_length, chapter_counts["medium"])

if __name__ == "__main__":
    # For standalone testing
    print("🧪 Testing Novel Fix Root Agent")
    asyncio.run(main()) 