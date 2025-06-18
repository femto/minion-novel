# Novel Writing Agent System

An intelligent novel writing system built with Google ADK, featuring multi-layered specialized agents to assist in the complete novel creation process.

## System Architecture

### Root Agent
- **Novel Write Agent**: Main coordinating agent that orchestrates the entire novel writing process

### Sub Agents

#### 1. Outline Agent
- Responsible for creating novel outlines
- Generates structured story outlines based on genre, theme, and target length
- Tool: `create_outline`

#### 2. Character Agent
- Responsible for creating detailed character profiles
- Includes background, personality, motivation, appearance, relationships, etc.
- Tool: `create_character_profile`

#### 3. Act Agent (Chapter Writing Agent)
A composite agent with sub-agents, containing the following specialized sub-agents:

##### 3.1 Opening Chapter Agent
- Specializes in writing opening chapters
- Focuses on strong beginnings, character introduction, world-building
- Tool: `write_opening_chapter`

##### 3.2 Action Chapter Agent
- Specializes in writing action and conflict scenes
- Focuses on pacing, tension, clear action descriptions
- Tool: `write_action_chapter`

##### 3.3 Dialogue Chapter Agent
- Specializes in writing dialogue-focused chapters
- Focuses on character voice, relationship dynamics, information revelation
- Tool: `write_dialogue_chapter`

##### 3.4 Climax Chapter Agent
- Specializes in writing climactic chapters
- Focuses on maximum tension, character resolution, thematic elevation
- Tool: `write_climax_chapter`

#### 4. Progress Agent
- Monitors novel writing progress
- Provides completion status updates and next step suggestions
- Tool: `get_novel_progress`

## Features

- **State Management**: Maintains novel project state across sessions
- **Specialized Division**: Each agent focuses on specific writing tasks
- **Hierarchical Structure**: Act Agent contains multiple specialized chapter writing sub-agents
- **Consistency Maintenance**: All agents share project state, ensuring character and plot consistency
- **Progress Tracking**: Real-time monitoring of writing progress and completion status

## Installation & Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API keys (in `.env` file):
```
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_KEY=your_azure_api_key
AZURE_API_VERSION=your_api_version
```

3. Run the system:
```bash
python agent.py
```

## Usage Examples

```python
# Start novel creation
"Help me start writing a fantasy novel about friendship and loyalty, target length should be medium"

# Create character profiles
"Create character profiles for the main protagonist and antagonist"

# Write opening chapter
"Write the opening chapter introducing the main character in a magical forest setting"

# Write action scene
"Write an action chapter with a sword fight between the protagonist and antagonist"

# Check progress
"What's my current progress on the novel?"
```

## Design Advantages

1. **Modular**: Each agent handles specific functions, easy to maintain and extend
2. **Specialized**: Different chapter types are handled by dedicated agents, improving writing quality
3. **Coordinated**: Root agent ensures all elements work together consistently
4. **Extensible**: Can easily add new chapter types or writing agents
5. **State-Driven**: Makes intelligent decisions about next actions based on project state 