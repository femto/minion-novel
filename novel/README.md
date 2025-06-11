# Novel Writing Agent System

一个基于Google ADK构建的智能小说写作系统，通过多层次的专业化agents来协助完整的小说创作流程。

## 系统架构

### Root Agent
- **Novel Write Agent**: 主要协调agent，统筹整个小说创作过程

### Sub Agents

#### 1. Outline Agent (大纲代理)
- 负责创建小说大纲
- 根据题材、主题和目标长度生成结构化故事大纲
- 工具: `create_outline`

#### 2. Character Agent (人物小传代理) 
- 负责创建详细的角色档案
- 包括背景、性格、动机、外貌、关系等
- 工具: `create_character_profile`

#### 3. Act Agent (章节写作代理)
这是一个有子代理的复合agent，包含以下专业化sub agents:

##### 3.1 Opening Chapter Agent (开篇章节代理)
- 专门写作开篇章节
- 注重强力开头、角色介绍、世界构建
- 工具: `write_opening_chapter`

##### 3.2 Action Chapter Agent (动作章节代理)  
- 专门写作动作和冲突场景
- 注重节奏、紧张感、清晰的动作描述
- 工具: `write_action_chapter`

##### 3.3 Dialogue Chapter Agent (对话章节代理)
- 专门写作以对话为主的章节
- 注重角色声音、关系动态、信息揭示
- 工具: `write_dialogue_chapter`

##### 3.4 Climax Chapter Agent (高潮章节代理)
- 专门写作高潮章节
- 注重最大张力、角色解决、主题升华
- 工具: `write_climax_chapter`

#### 4. Progress Agent (进度跟踪代理)
- 监控小说写作进度
- 提供完成状态更新和下一步建议
- 工具: `get_novel_progress`

## 功能特性

- **状态管理**: 跨会话保持小说项目状态
- **专业化分工**: 每个agent专注于特定的写作任务
- **层次化结构**: Act Agent下有多个专业化的章节写作sub agents
- **一致性维护**: 所有agents共享项目状态，确保角色和情节一致性
- **进度跟踪**: 实时监控写作进度和完成情况

## 安装使用

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 配置API密钥 (在`.env`文件中):
```
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_KEY=your_azure_api_key
AZURE_API_VERSION=your_api_version
```

3. 运行系统:
```bash
python agent.py
```

## 使用示例

```python
# 启动小说创作
"Help me start writing a fantasy novel about friendship and loyalty, target length should be medium"

# 创建角色档案
"Create character profiles for the main protagonist and antagonist"

# 写作开篇章节
"Write the opening chapter introducing the main character in a magical forest setting"

# 写作动作场景
"Write an action chapter with a sword fight between the protagonist and antagonist"

# 检查进度
"What's my current progress on the novel?"
```

## 设计优势

1. **模块化**: 每个agent负责特定功能，易于维护和扩展
2. **专业化**: 不同类型的章节由专门的agent处理，提高写作质量
3. **协调性**: Root agent确保所有元素协调一致
4. **可扩展**: 可以easily添加新的chapter types或writing agents
5. **状态驱动**: 基于项目状态智能决策下一步动作 