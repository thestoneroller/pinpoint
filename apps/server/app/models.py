from pydantic import BaseModel, Field, HttpUrl
from typing import List, Annotated, TypedDict
from fastapi import Query


class IssueQueryResult(BaseModel):
    technology: str
    queries: List[str]
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
