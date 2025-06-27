import asyncio
import os
from dataclasses import dataclass
from typing import Optional, List
from tavily import AsyncTavilyClient, TavilyClient


@dataclass(frozen=True, kw_only=True)
class SearchResult:
    title: str
    link: str
    content: str
    raw_content: Optional[str] = None

    def __str__(self, include_raw=True):
        result = f"Title: {self.title}\n" f"Link: {self.link}\n" f"Content: {self.content}"
        if include_raw and self.raw_content:
            result += f"\nRaw Content: {self.raw_content}"
        return result

    def short_str(self):
        return self.__str__(include_raw=False)


@dataclass(frozen=True, kw_only=True)
class SearchResults:
    results: List[SearchResult]

    def __str__(self, short=False):
        if short:
            result_strs = [result.short_str() for result in self.results]
        else:
            result_strs = [str(result) for result in self.results]
        return "\n\n".join(f"[{i+1}] {result_str}" for i, result_str in enumerate(result_strs))

    def __add__(self, other):
        return SearchResults(results=self.results + other.results)

    def short_str(self):
        return self.__str__(short=True)


@dataclass(frozen=True, kw_only=True)
class DeepResearchResult(SearchResult):
    """Extended SearchResult for deep research with filtered content"""
    filtered_raw_content: str

    def __str__(self):
        return f"Title: {self.title}\n" f"Link: {self.link}\n" f"Refined Content: {self.filtered_raw_content[:1000]}..."

    def short_str(self):
        return f"Title: {self.title}\nLink: {self.link}\nContent: {self.content[:500]}..."


@dataclass(frozen=True, kw_only=True)
class DeepResearchResults:
    results: List[DeepResearchResult]

    def __str__(self, short=False):
        if short:
            result_strs = [result.short_str() for result in self.results]
        else:
            result_strs = [str(result) for result in self.results]
        return "\n\n".join(f"[{i+1}] {result_str}" for i, result_str in enumerate(result_strs))

    def __add__(self, other):
        return DeepResearchResults(results=self.results + other.results)

    def short_str(self):
        return self.__str__(short=True)

    def dedup(self):
        """Remove duplicate results based on link"""
        seen_links = set()
        unique_results = []
        for result in self.results:
            if result.link not in seen_links:
                seen_links.add(result.link)
                unique_results.append(result)
        return DeepResearchResults(results=unique_results)


def extract_tavily_results(response) -> SearchResults:
    """Extract key information from Tavily search results."""
    results = []
    for item in response.get("results", []):
        results.append(
            SearchResult(
                title=item.get("title", ""),
                link=item.get("url", ""),
                content=item.get("content", ""),
                raw_content=item.get("raw_content", ""),
            )
        )
    return SearchResults(results=results)


def tavily_search(query: str, max_results=3, include_raw: bool = True) -> SearchResults:
    """
    Perform a search using the Tavily Search API.

    Parameters:
        query (str): The search query.
        max_results (int): Maximum number of results to return.
        include_raw (bool): Whether to include raw content.

    Returns:
        SearchResults: Formatted search results with title, link, and snippet.
    """
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set")

    client = TavilyClient(api_key)

    response = client.search(
        query=query, 
        search_depth="basic", 
        max_results=max_results, 
        include_raw_content=include_raw
    )

    return extract_tavily_results(response)


async def atavily_search_results(query: str, max_results=3, include_raw: bool = True) -> SearchResults:
    """
    Perform asynchronous search using the Tavily Search API.

    Parameters:
        query (str): The search query.
        max_results (int): Maximum number of results to return.
        include_raw (bool): Whether to include raw content.

    Returns:
        SearchResults: Formatted search results.
    """
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set")

    client = AsyncTavilyClient(api_key)

    response = await client.search(
        query=query, 
        search_depth="basic", 
        max_results=max_results, 
        include_raw_content=include_raw
    )

    return extract_tavily_results(response) 