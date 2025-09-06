from fastapi import APIRouter, Request
from ...services.github import search_issues, get_issues_comments, get_repository
from ...utils import check_repo_exists, event_message
from fastapi.responses import StreamingResponse
from ...services.gemini import generate_issue_queries, generate_streaming_answer
from typing import Optional
import time

router = APIRouter()


async def search_stream(*, repo: Optional[str] = None, query: str, request: Request):
    """Search for issues in a GitHub repository."""

    start_time = time.time()

    # Use Gemini to generate 3 queries to search in Github Issues
    queries = await generate_issue_queries(request=request, user_query=query)
    yield event_message("search_queries", data=queries.model_dump())

    # Get repository name
    if not repo:
        repo = await get_repository(technology=queries.technology)
    else:
        repo_exists = await check_repo_exists(repo=repo)
        if not repo_exists:
            repo = await get_repository(technology=repo)

    yield event_message("get_repository", {"repo": repo})

    # Search for issues using Github REST API
    issues, issue_numbers = await search_issues(repo=repo, queries=queries)
    yield event_message("search_issues", {"total_issues": len(issue_numbers)})

    comments = await get_issues_comments(repo=repo, issue_numbers=issue_numbers)
    yield event_message("get_issues_comments", {"total_comments": len(comments)})

    # Use Gemini to generate an answer based on the collected data
    yield event_message(
        "generate_streaming_answer_start",
        {"message": "Generating AI response..."},
    )

    async for text_chunk in generate_streaming_answer(
        request=request,
        user_query=query,
        issues=issues,
        comments=comments,
    ):
        yield event_message("streaming_answer_chunk", {"text": text_chunk})

    end_time = time.time()
    elapsed_time = end_time - start_time

    yield event_message(
        "streaming_answer_end",
        {
            "message": "Response complete",
            "elapsed_time_seconds": round(elapsed_time, 2),
        },
    )


@router.post("/search")
async def search(*, repo: Optional[str] = None, query: str, request: Request):
    return StreamingResponse(
        search_stream(repo=repo, query=query, request=request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
