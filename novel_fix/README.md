# Novel Fix - Fixed Workflow Novel Writing Agent

基于Google ADK的**Workflow Agent**实现的固定流程小说创作系统。

## 🎯 设计理念

与`novel`目录的动态决策不同，`novel_fix`使用**固定的、预定义的工作流程**来创作小说，无需用户交互指导每一步。

## 🔄 固定流程（使用SequentialAgent）

根据[ADK Workflow Agents文档](https://google.github.io/adk-docs/agents/workflow-agents/)，本系统实现以下固定执行顺序：

1. **📋 大纲创建** (`OutlineAgent`)
   - 创建三幕结构
   - 确定章节数量和结构
   - 定义关键情节点

2. **👥 人物小传** (`CharacterAgent`) 
   - 主角详细档案
   - 反派角色设定
   - 2-3个支撑角色

3. **📖 Act 1 写作** (`Act1Agent` - SequentialAgent)
   - Chapter 1: 角色和世界介绍
   - Chapter 2: 世界构建延续
   - Chapter 3: 引发事件
   - Chapter 4: 第一幕结束

4. **📖 Act 2 写作** (`Act2Agent` - SequentialAgent)
   - Chapter 1-2: 上升行动
   - Chapter 3-4: 冲突发展
   - Chapter 5-6: 中点危机

5. **📖 Act 3 写作** (`Act3Agent` - SequentialAgent)
   - Chapter 1: 高潮准备
   - Chapter 2: 高潮场面
   - Chapter 3-4: 下降行动和解决

## 🆚 与novel目录的对比

| 特性 | novel (动态) | novel_fix (固定) |
|------|-------------|-----------------|
| **流程控制** | LLM动态决策 | SequentialAgent固定流程 |
| **用户交互** | 需要对话指导 | 一次输入，自动执行 |
| **执行顺序** | 可变，依赖LLM判断 | 严格按序：大纲→人物→Act1→Act2→Act3 |
| **可预测性** | 不确定 | 完全可预测 |
| **适用场景** | 交互式创作 | 批量生产、自动化 |
| **基础技术** | Sub-agents + LLM coordination | Workflow Agents (SequentialAgent) |

## 🚀 使用方法

### 1. ADK Web 交互（推荐）
```bash
cd novel_fix
adk web
```
然后在浏览器中与Novel Fix Web Agent交互：
- "What is Novel Fix and how does it work?"
- "Start a fantasy novel about friendship and courage, medium length"
- "Check the current pipeline status"

### 2. 命令行测试
```bash
cd novel_fix
python agent.py  # 测试root agent
python web_agent.py  # 测试web agent
```

### 3. 编程接口
```python
from novel_fix.agent import create_and_run_novel

# 自动执行完整小说创作流程
await create_and_run_novel(
    genre="fantasy",
    theme="friendship and courage", 
    target_length="medium"
)
```

### 4. 自定义流程
```python
from novel_fix.agent import create_novel_pipeline_agent

# 创建特定的流程agent
pipeline = create_novel_pipeline_agent(
    genre="science fiction",
    theme="technological ethics",
    target_length="short"  # short/medium/long
)
```

## 📊 支持的配置

### 类型长度
- **short**: ~50k words (12章: 4+4+4)
- **medium**: ~80k words (18章: 6+6+6) 
- **long**: ~120k words (24章: 8+8+8)

### 环境配置
支持Azure OpenAI和Google Gemini：
```env
# Azure配置
USE_AZURE=true
AZURE_MODEL_NAME=gpt-4.1
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_API_VERSION=2024-02-15-preview

# Google配置  
USE_AZURE=false
GOOGLE_API_KEY=your-google-key
GOOGLE_MODEL_NAME=gemini-2.0-flash-exp
```

## 🔧 技术实现

基于Google ADK的核心Workflow Agent类型：

1. **SequentialAgent**: 确保严格的执行顺序
2. **LlmAgent**: 每个步骤的具体执行
3. **output_key**: 在不同步骤间传递数据

参考ADK文档：
- [Workflow Agents](https://google.github.io/adk-docs/agents/workflow-agents/)
- [Sequential Agents](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)

## 💡 优势

1. **可预测性**: 每次运行都遵循相同流程
2. **可靠性**: 确保任务按正确顺序执行
3. **结构化**: 清晰的控制流程，易于调试
4. **自动化**: 无需人工干预，适合批量处理
5. **一致性**: 输出格式和质量更加统一

## 🎯 适用场景

- 内容工厂的批量小说生产
- 需要标准化流程的创作
- 教学和演示固定写作流程
- 对比测试不同的创作方法 