import logging

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI 

from research_agent.state import ResearchState
from research_agent.config import settings
from research_agent.tools import search_web
from research_agent.source_quality import score_sources

logger = logging.getLogger(__name__)

llm = ChatGoogleGenerativeAI(
    model=settings.model_name,
    google_api_key=settings.google_api_key
)

def query_planner_node(state: ResearchState) -> ResearchState:
    topic = state['topic']

    prompt = f"""
    You are a research query planner.
    
    Topic: {topic}

    Generate 3 good web search queries to find relevant information about this topic.

    Rules:
    - Return only the queries.
    - One query per line
    - Do not use numbering
    """

    response = llm.invoke(prompt)

    queries = [
        line.strip() for line in response.content.splitlines() if line.strip()
    ]

    if not queries:
        logger.warning(f"No queries generated for topic: {topic}")
        queries = [topic]

    logger.info(f"Generated queries for topic", len(queries))

    return {
        **state,
        "search_queries": queries[:3]}



def web_search_node(state: ResearchState) -> ResearchState:
    all_sources = []

    for query in state['search_queries']:
        sources = search_web(query, max_results=3)
        all_sources.extend(sources)

    seen_urls = set()
    deduped_sources = []


    for source in all_sources:
        url = source['url']

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)
        deduped_sources.append(source)

    logger.info('Collected %d unique sources', len(deduped_sources))

    return {
        **state,
        'sources': deduped_sources
    }
    

def source_quality_node(state: ResearchState) -> ResearchState:
    scored_sources = score_sources(state['sources'])

    reliable_sources = [
        source 
        for source in scored_sources
        if source['is_reliable']
    ]

    logger.info(
        "Scored %d sources; kept %d reliable sources",
        len(scored_sources),
        len(reliable_sources)
    )

    return {
        **state,
        "scored_sources": reliable_sources
    }



def note_taker_node(state: ResearchState) -> ResearchState:
    topic = state['topic']
    sources = state['scored_sources']

    source_text = "\n\n".join(
        f"""
        Title: {source["title"]}
        URL: {source["url"]}
        Type: {source['source_type']}
        Quality score: {source['quality_score']}
        Quality reason: {source['quality_reason']}
        Snippet: {source["snippet"]}
        """
        for source in sources
    )

    prompt = f"""
    You are a careful research assistant.

    Topic:
    {topic}

    Sources:
    {source_text}

    Extract useful research notes from the sources

    Rules:
    - Use only information supported by the provided source snippets.
    - Do not invent facts
    - Keep notes concise
    - Mention the source URL next to each note
    """

    response = llm.invoke(prompt)

    return {
        **state,
        "notes": [response.content]
    }


def writer_node(state: ResearchState) -> ResearchState:
    topic = state['topic']
    notes = state['notes']

    prompt = f"""
    Write a short structured research draft about this topic:

    Topic: {topic}

    Notes:
    {notes}

    Structure:
    - Title
    - Introduction
    - Main points
    - Conclusions

    Rules:
    - Use only the provided notes
    - Include source URLs when making factual claims.
    - If evidence is weak say so.
    """

    response = llm.invoke(prompt)

    return {
        **state,
        "draft": response.content
    }


def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node('query_planner', query_planner_node)
    graph.add_node('web_search', web_search_node)
    graph.add_node('source_quality', source_quality_node)
    graph.add_node('note_taker', note_taker_node)
    graph.add_node("writer", writer_node)

    graph.set_entry_point("query_planner")

    graph.add_edge("query_planner", "web_search")
    graph.add_edge('web_search', 'source_quality')
    graph.add_edge('source_quality', 'note_taker')
    graph.add_edge('note_taker', 'writer')
    graph.add_edge("writer", END)

    return graph.compile()