from pydantic import BaseModel
from typing import List, Literal, Annotated
from fastapi import Query


class IssueQueryResult(BaseModel):
    technology: str
    queries: List[str]
    intent: Literal[
        "bug_report",
        "feature_request",
        "help_needed",
        "configuration",
        "performance",
        "compatibility",
        "general_info",
    ]
    confidence: float


class SearchRequest(BaseModel):
    repo: Annotated[str, Query(pattern=r"^[^/\s]+/[^/\s]+$")]
    query: Annotated[str, Query(min_length=30)]
