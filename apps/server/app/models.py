from pydantic import BaseModel, Field, HttpUrl
from typing import List, Annotated, TypedDict, Optional
from fastapi import Query


class IssueQueryResult(BaseModel):
    technology: str
    queries: List[str]
    confidence: float


class SearchRequest(BaseModel):
    repo: Optional[Annotated[str, Query(pattern=r"^[^/\s]+/[^/\s]+$")]] = None
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
