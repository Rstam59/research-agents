from typing import TypedDict, List 


class ResearchState(TypedDict):
    topic: str 
    notes: List[str]
    draft: str 