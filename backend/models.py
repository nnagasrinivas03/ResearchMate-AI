from typing import TypedDict, List, Dict, Any


class ResearchState(TypedDict, total=False):
    topic: str

    web_sources: List[Dict[str, Any]]
    arxiv_sources: List[Dict[str, Any]]
    semantic_sources: List[Dict[str, Any]]

    sources: List[Dict[str, Any]]

    evidence: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]

    report: str

    events: List[Dict[str, Any]]