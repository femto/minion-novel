import os
import traceback

import asyncio
import json
import hashlib
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from google.adk.agents import Agent, LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools.tool_context import ToolContext
from google.genai import types
import google.generativeai as genai

from .deep_research_types import tavily_search, atavily_search_results, DeepResearchResult, DeepResearchResults

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

async def call_llm_async(prompt: str) -> str:
    """Helper function to call LLM for content generation."""
    try:
        if USE_AZURE:
            llm = create_llm()
            from google.adk.models.llm_request import LlmRequest
            
            content = types.Content(role='user', parts=[types.Part(text=prompt)])
            config = types.GenerateContentConfig(tools=[])  # Create empty config
            llm_request = LlmRequest(contents=[content], config=config)
            
            full_response = ""
            async for response in llm.generate_content_async(llm_request):
                if response.content and response.content.parts:
                    full_response += response.content.parts[0].text
            return full_response
        else:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel(GOOGLE_MODEL_NAME)
            response = await model.generate_content_async(prompt)
            return response.text
    except Exception as e:
        print(f"Error calling LLM: {e}")
        print(f"Full error details:\n{traceback.format_exc()}")
        return f"[LLM Error: Could not generate content. {str(e)}]"

# Research Data Models
from pydantic import BaseModel
from typing import List

class ResearchQuery(BaseModel):
    query: str
    priority: int = 1
    results: List[dict] = []

class ResearchResult(BaseModel):
    title: str
    content: str
    source: str
    relevance_score: float = 0.0

class ResearchSession(BaseModel):
    topic: str
    queries: List[ResearchQuery] = []
    all_results: List[ResearchResult] = []
    filtered_results: List[ResearchResult] = []
    final_report: str = ""

# Deep Research Tools
async def generate_research_queries(topic: str, tool_context: ToolContext) -> dict:
    """Generate initial research queries based on the topic."""
    print(f"--- Tool: generate_research_queries for topic: {topic} ---")
    
    prompt = f"""Given the research topic: "{topic}"

Generate 5-8 specific, focused research queries that would help gather comprehensive information about this topic. 

Guidelines:
- Make queries specific and actionable
- Cover different angles and aspects of the topic
- Include both factual and analytical perspectives
- Ensure queries are suitable for web search or database lookup

Format your response as a JSON list of query strings:
["query1", "query2", "query3", ...]

Topic: {topic}"""

    response = await call_llm_async(prompt)
    
    try:
        # Try to extract JSON from response
        import re
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            queries = json.loads(json_match.group())
        else:
            # Fallback: split by lines and clean
            queries = [q.strip('- ').strip() for q in response.split('\n') if q.strip() and not q.strip().startswith('[') and not q.strip().endswith(']')]
            queries = [q for q in queries if len(q) > 10][:8]
    except:
        # Fallback queries
        queries = [
            f"What is {topic}?",
            f"History and background of {topic}",
            f"Current developments in {topic}",
            f"Key challenges in {topic}",
            f"Future trends in {topic}"
        ]
    
    # Store in session state
    if "research_session" not in tool_context.state:
        tool_context.state["research_session"] = ResearchSession(topic=topic)
    
    session = tool_context.state["research_session"]
    session.queries = [ResearchQuery(query=q) for q in queries[:8]]
    
    print(f"--- Tool: Generated {len(queries)} research queries ---")
    return {"status": "success", "queries": queries, "count": len(queries)}

async def tavily_web_search(query: str, tool_context: ToolContext) -> dict:
    """Perform real web search using Tavily API."""
    print(f"--- Tool: tavily_web_search for query: {query} ---")
    
    try:
        # Use Tavily API for real web search
        search_results_data = await atavily_search_results(query, max_results=5, include_raw=True)
        
        search_results = []
        for result in search_results_data.results:
            # Filter and summarize content using LLM for better relevance
            if result.raw_content:
                summarize_prompt = f"""Summarize the following content in relation to the search query: "{query}"

Content: {result.raw_content[:2000]}...

Provide a concise summary (2-3 sentences) that highlights the most relevant information for the search query."""

                summary = await call_llm_async(summarize_prompt)
                filtered_content = summary
            else:
                filtered_content = result.content

            search_results.append({
                "title": result.title,
                "content": filtered_content,
                "source": result.link,
                "relevance_score": 0.9  # Default high relevance for Tavily results
            })
        
        print(f"--- Tool: Tavily found {len(search_results)} search results ---")
        
    except Exception as e:
        print(f"--- Tool: Tavily search failed: {e}, falling back to simulated results ---")
        # Fallback to simulated results if Tavily fails
        search_results = [{
            "title": f"Research Result for {query}",
            "content": f"Fallback: Information related to {query}. Unable to fetch real search results.",
            "source": "fallback.com",
            "relevance_score": 0.6
        }]
    
    # Store results in session
    session = tool_context.state.get("research_session")
    if session:
        for result in search_results:
            research_result = ResearchResult(
                title=result["title"],
                content=result["content"],
                source=result["source"],
                relevance_score=result["relevance_score"]
            )
            session.all_results.append(research_result)
    
    print(f"--- Tool: Stored {len(search_results)} search results in session ---")
    return {"status": "success", "results": search_results, "count": len(search_results)}

async def filter_and_rank_results(topic: str, tool_context: ToolContext) -> dict:
    """Filter and rank research results by relevance to the topic."""
    print(f"--- Tool: filter_and_rank_results for topic: {topic} ---")
    
    session = tool_context.state.get("research_session")
    if not session or not session.all_results:
        return {"status": "error", "message": "No research results to filter"}
    
    # Create summary of all results for filtering
    results_summary = ""
    for i, result in enumerate(session.all_results):
        results_summary += f"Result {i+1}:\nTitle: {result.title}\nContent: {result.content[:200]}...\nSource: {result.source}\n\n"
    
    filter_prompt = f"""Given the research topic: "{topic}"

Review the following research results and:
1. Rank them by relevance to the topic (1-10 scale)
2. Identify the top 5-8 most relevant results
3. Provide a brief explanation of why each selected result is relevant

Research Results:
{results_summary}

Format your response as JSON:
{{
  "selected_results": [
    {{
      "result_index": 1,
      "relevance_score": 9.2,
      "reason": "..."
    }}
  ],
  "filtering_summary": "..."
}}

Topic: {topic}"""

    response = await call_llm_async(filter_prompt)
    
    try:
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            filter_result = json.loads(json_match.group())
            selected_indices = [r["result_index"]-1 for r in filter_result["selected_results"]]
        else:
            # Fallback - select top results
            selected_indices = list(range(min(6, len(session.all_results))))
    except:
        selected_indices = list(range(min(6, len(session.all_results))))
    
    # Filter results
    session.filtered_results = [session.all_results[i] for i in selected_indices if i < len(session.all_results)]
    
    print(f"--- Tool: Filtered to {len(session.filtered_results)} relevant results ---")
    return {
        "status": "success", 
        "filtered_count": len(session.filtered_results),
        "total_count": len(session.all_results)
    }

async def generate_research_report(topic: str, tool_context: ToolContext) -> dict:
    """Generate a comprehensive research report based on filtered results."""
    print(f"--- Tool: generate_research_report for topic: {topic} ---")
    
    session = tool_context.state.get("research_session")
    if not session or not session.filtered_results:
        return {"status": "error", "message": "No filtered results available for report generation"}
    
    # Compile research content
    research_content = ""
    for i, result in enumerate(session.filtered_results):
        research_content += f"Source {i+1}: {result.title}\n{result.content}\n[{result.source}]\n\n"
    
    report_prompt = f"""Create a comprehensive research report on the topic: "{topic}"

Use the following research sources to create a well-structured, informative report:

{research_content}

Structure your report with:
1. Executive Summary
2. Key Findings (organized by themes/subtopics)
3. Detailed Analysis
4. Conclusions and Implications
5. Sources/References

Make the report professional, well-organized, and comprehensive while being accessible to a general audience.

Topic: {topic}"""

    report = await call_llm_async(report_prompt)
    
    # Store final report
    session.final_report = report
    
    print(f"--- Tool: Generated comprehensive research report ---")
    return {
        "status": "success", 
        "report": report,
        "sources_used": len(session.filtered_results)
    }

def get_research_progress(tool_context: ToolContext) -> dict:
    """Get current research progress and session information."""
    print(f"--- Tool: get_research_progress called ---")
    
    session = tool_context.state.get("research_session")
    if not session:
        return {"status": "no_session", "message": "No active research session"}
    
    progress = {
        "topic": session.topic,
        "queries_generated": len(session.queries),
        "total_results": len(session.all_results),
        "filtered_results": len(session.filtered_results),
        "report_ready": bool(session.final_report),
        "current_step": "initialized"
    }
    
    if session.queries:
        progress["current_step"] = "queries_generated"
    if session.all_results:
        progress["current_step"] = "search_completed"
    if session.filtered_results:
        progress["current_step"] = "results_filtered"
    if session.final_report:
        progress["current_step"] = "report_completed"
    
    return {"status": "success", "progress": progress}

# Research tools - pass functions directly to the Agent
research_tools = [
    generate_research_queries,
    tavily_web_search,
    filter_and_rank_results,
    generate_research_report,
    get_research_progress
]

def create_deep_research_agent():
    """Creates the main deep research agent."""
    llm = create_llm()
    
    instruction = """You are a Deep Research Agent capable of conducting comprehensive research on any topic using real web search.

Your workflow:
1. Generate specific research queries for the given topic
2. Search for information using Tavily web search API
3. Filter and rank results by relevance 
4. Generate a comprehensive research report

Available tools:
- generate_research_queries: Create focused search queries
- tavily_web_search: Search the web using Tavily API for real, current information
- filter_and_rank_results: Filter results by relevance and quality
- generate_research_report: Create final comprehensive research report
- get_research_progress: Check current research status

Process:
1. Start by generating research queries for the topic
2. Search each query using real web search to gather current information
3. Filter results to keep only the most relevant and high-quality sources
4. Generate a professional research report with citations

Always provide thorough, well-sourced research with clear structure, analysis, and proper citations to web sources."""

    return Agent(
        model=llm,
        name="deep_research_agent",
        instruction=instruction,
        description="Conducts comprehensive research on topics and generates detailed reports",
        tools=research_tools
    )

async def call_agent_async(query: str, runner: Runner, user_id: str, session_id: str):
    """Call the deep research agent asynchronously."""
    print(f"--- Starting Deep Research Agent for query: {query} ---")
    
    try:
        from google.genai.types import Content, Part
        
        # Create message content
        content = Content(parts=[Part(text=query)], role="user")
        
        # Get the final response from the event stream
        final_response_text = "(No final response)"
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
                break
        
        print(f"--- Deep Research Agent completed ---")
        return final_response_text
    except Exception as e:
        print(f"Error in deep research agent: {e}")
        return f"Error: {str(e)}"
root_agent = agent = create_deep_research_agent()

async def main():
    """Main function to test the deep research agent."""
    # Create and configure the agent
    agent = create_deep_research_agent()
    
    # Set up session service and runner
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, session_service=session_service, app_name="deep_research_test")
    
    # Test queries
    test_queries = [
        "artificial intelligence in healthcare",
        "climate change impacts on agriculture", 
        "blockchain technology applications",
        "renewable energy trends 2024"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing Deep Research Agent with: {query}")
        print(f"{'='*60}")
        
        result = await call_agent_async(
            query=f"Research the topic: {query}",
            runner=runner,
            user_id="test_user",
            session_id=f"session_{hash(query) % 10000}"
        )
        
        print(f"\nResult: {result}")
        print(f"\n{'='*60}")

if __name__ == "__main__":
    asyncio.run(main()) 