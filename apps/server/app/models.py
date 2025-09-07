from pydantic import BaseModel, Field, HttpUrl
from typing import List, Literal, Annotated, TypedDict
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


class CommentData(TypedDict):
    body: str
    username: str
    comment_url: str


class IssueWithComments(BaseModel):
    issue_number: int
    title: str
    issue_url: HttpUrl = Field(alias="html_url")
    body: str
    comments: List[CommentData]
