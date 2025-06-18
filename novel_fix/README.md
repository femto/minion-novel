# Novel Fix - Fixed Workflow Novel Writing System

> **Simple. Automated. Predictable.**

Novel Fix is a **fixed workflow** novel writing system that automatically generates complete novels from a single user input. Unlike dynamic systems that require user guidance, Novel Fix follows a predetermined 6-step sequential process to produce professional-quality novels.

## ✨ Key Features

- 🤖 **Fully Automated**: One input → Complete novel
- 📝 **Fixed 6-Step Pipeline**: Parameter extraction → Outline → Characters → Act 1 → Act 2 → Act 3  
- 🎯 **Smart Parameter Detection**: Automatically extracts genre, theme, and length from natural language
- 📚 **Professional Structure**: 3-act format with proper chapter distribution (14/20/26 chapters)
- 🔄 **Consistent Results**: Same reliable workflow every time
- 🚀 **Zero User Intervention**: Set it and forget it approach

## 🆚 Novel vs Novel Fix

| Feature | Novel (Dynamic) | Novel Fix (Fixed) |
|---------|----------------|-------------------|
| **User Input** | Ongoing dialogue guidance | Single story request |
| **Workflow** | LLM-based decisions | Predetermined sequence |
| **Predictability** | Variable outcomes | Consistent results |
| **Use Case** | Interactive creation | Batch production |
| **Complexity** | High (requires guidance) | Low (fully automated) |

---

## 🎯 Design Philosophy

Unlike the dynamic decision-making in the `novel` directory, `novel_fix` uses a **fixed, predefined workflow** to create novels without requiring user interaction at each step.

## 🔄 Fixed Workflow (Using SequentialAgent)

Based on the [ADK Workflow Agents documentation](https://google.github.io/adk-docs/agents/workflow-agents/), this system implements the following fixed execution order:

1. **📋 Outline Creation** (`OutlineAgent`)
   - Create three-act structure
   - Determine chapter count and structure
   - Define key plot points

2. **👥 Character Profiles** (`CharacterAgent`) 
   - Detailed protagonist profile
   - Antagonist character setup
   - 2-3 supporting characters

3. **📖 Act 1 Writing** (`Act1Agent` - SequentialAgent)
   - Chapter 1: Character and world introduction
   - Chapter 2: World-building continuation
   - Chapter 3: Inciting incident
   - Chapter 4: Act 1 conclusion

4. **📖 Act 2 Writing** (`Act2Agent` - SequentialAgent)
   - Chapter 1-2: Rising action
   - Chapter 3-4: Conflict development
   - Chapter 5-6: Midpoint crisis

5. **📖 Act 3 Writing** (`Act3Agent` - SequentialAgent)
   - Chapter 1: Climax preparation
   - Chapter 2: Climax scene
   - Chapter 3-4: Falling action and resolution

## 🚀 Usage Methods

### 1. ADK Web Interaction (Recommended)
```bash
cd novel_fix
adk web
```
Then interact with Novel Fix Web Agent in browser:
- "What is Novel Fix and how does it work?"
- "Start a fantasy novel about friendship and courage, medium length"
- "Check the current pipeline status"

### 2. Command Line Testing
```bash
cd novel_fix
python agent.py  # Test root agent
python web_agent.py  # Test web agent
```

### 3. Programming Interface
```python
from novel_fix.agent import create_and_run_novel

# Auto-execute complete novel writing workflow
await create_and_run_novel(
    genre="fantasy",
    theme="friendship and courage", 
    target_length="medium"
)
```

### 4. Custom Workflow
```python
from novel_fix.agent import create_novel_pipeline_agent

# Create specific workflow agent
pipeline = create_novel_pipeline_agent(
    genre="science fiction",
    theme="technological ethics",
    target_length="short"  # short/medium/long
)
```

## 📊 Supported Configurations

### Length Types
- **short**: ~50k words (14 chapters: 4+6+4)
- **medium**: ~80k words (20 chapters: 6+8+6) 
- **long**: ~120k words (26 chapters: 8+10+8)

### Environment Configuration
Supports Azure OpenAI and Google Gemini:
```env
# Azure configuration
USE_AZURE=true
AZURE_MODEL_NAME=gpt-4.1
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_API_VERSION=2024-02-15-preview

# Google configuration  
USE_AZURE=false
GOOGLE_API_KEY=your-google-key
GOOGLE_MODEL_NAME=gemini-2.0-flash-exp
```

## 🔧 Technical Implementation

Based on Google ADK's core Workflow Agent types:

1. **SequentialAgent**: Ensures strict execution order
2. **LlmAgent**: Specific execution for each step
3. **output_key**: Pass data between different steps

Reference ADK documentation:
- [Workflow Agents](https://google.github.io/adk-docs/agents/workflow-agents/)
- [Sequential Agents](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)

## 💡 Advantages

1. **Predictability**: Same workflow followed every time
2. **Reliability**: Ensures tasks execute in correct order
3. **Structured**: Clear control flow, easy to debug
4. **Automated**: No manual intervention needed, suitable for batch processing
5. **Consistent**: More uniform output format and quality

## 🎯 Use Cases

- Batch novel production for content factories
- Standardized workflow creation needs
- Teaching and demonstrating fixed writing processes
- Comparative testing of different creation methods

## Root Agent Creation Methods

The Novel Fix system now uses a **simple SequentialAgent structure**:

### Single Method: Sequential Pipeline

```python
from novel_fix.agent import create_root_agent

# Creates a SequentialAgent with all steps in fixed order
root_agent = create_root_agent()
```

**Structure:**
```
novel_fix_sequential_pipeline
├── 1. parameter_extractor (extracts genre, theme, length from user input)
├── 2. outline_creator (creates 3-act novel outline)
├── 3. character_developer (develops protagonist, antagonist, supporting characters)
├── 4. act_1_writer (writes all Act 1 chapters)
├── 5. act_2_writer (writes all Act 2 chapters)
└── 6. act_3_writer (writes all Act 3 chapters)
```

**Features:**
- ✅ **One input, complete novel output**: User provides story idea, system produces full novel
- ✅ **Automatic parameter extraction**: Detects genre, theme, length from natural language
- ✅ **Fixed workflow**: Same predictable steps every time
- ✅ **No user intervention**: Fully automated from start to finish
- ✅ **Professional structure**: 3-act format with proper chapter distribution

**Example user inputs:**
- "I want to write a mystery novel about a detective solving crimes in a small town"
- "Create a science fiction story about space exploration with medium length"
- "Write a short romance novel about finding love"

### Parameter Extraction Details

The first agent automatically extracts:

- **Genre**: fantasy, science fiction, mystery, romance, thriller, horror, historical, adventure, drama
- **Length**: short (14 chapters), medium (20 chapters), long (26 chapters)  
- **Theme**: From patterns like "about X", "theme: X", "story about X"

**Default values (if not specified):**
- Genre: "fantasy"
- Theme: "adventure and discovery"
- Length: "medium" 