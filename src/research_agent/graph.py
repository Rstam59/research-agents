from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI 

from research_agent.state import ResearchState
from research_agent.config import settings

llm = ChatGoogleGenerativeAI(
    model=settings.model_name,
    google_api_key=settings.google_api_key
)

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