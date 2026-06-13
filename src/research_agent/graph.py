import logging

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI 

from research_agent.state import ResearchState
from research_agent.config import settings

from research_agent.tools import search_web

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

def researcher_node(state: ResearchState) -> ResearchState:
    topic = state['topic']

    prompt = f"""
    You are a careful research assistant

    Topic: {topic}

    Give 5 important research notes about this topic.
    Keep them factual and concise
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
    - Introduction
    - Main points
    - Conclusions
    """

    response = llm.invoke(prompt)

    return {
        **state,
        "draft": response.content
    }


def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)

    graph.set_entry_point("researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", END)

    return graph.compile()