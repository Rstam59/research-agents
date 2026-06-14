from typing import TypedDict, List 

class Source(TypedDict):
    title: str
    url: str
    snippet: str


class ScoredSource(Source):
    quality_score: float
    quality_reason: str
    source_type: str
    is_reliable: bool


class ResearchState(TypedDict):
    topic: str 
    search_queries: List[str]
    sources: List[Source]
    scored_sources: List[ScoredSource]
    notes: List[str]
    draft: str 