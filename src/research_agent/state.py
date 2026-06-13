from typing import TypedDict, List 

class Source(TypedDict):
    title: str
    url: str
    snippet: str

class ResearchState(TypedDict):
    topic: str 
    search_queries: List[str]
    sources: List[Source]
    notes: List[str]
    draft: str 