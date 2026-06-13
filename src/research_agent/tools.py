import logging 
from ddgs import DDGS
from typing import List

from research_agent.state import Source 

logger = logging.getLogger(__name__)

def search_web(query: str, max_results: int = 5) -> list[Source]:
    """"
    Search the web using DuckDuckGo and return a list of sources.
    """

    logger.info(f"Searching the web for query: {query}")

    sources: List[Source] = []

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)

            for result in results:
                source = Source(
                    title=result.get('title', ''),
                    url=result.get('href', ''),
                    snippet=result.get('body', '')
                )
                sources.append(source)
    except Exception:
        logger.exception("Web search failed for query: {query}")
    
    return sources