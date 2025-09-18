import time

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from ...models import SearchRequest
from ...services.gemini import generate_issue_queries, generate_streaming_answer
from ...services.github import get_issues_with_comments, get_repository, search_issues
from ...utils import check_repo_exists, event_message

router = APIRouter()


async def search_stream(search_request: SearchRequest, request: Request):
    """Search for issues in a GitHub repository."""

    start_time = time.time()

    # Use Gemini to generate 3 queries to search in Github Issues
    queries_response = await generate_issue_queries(
        request=request, user_query=search_request.query
    )

    # Check if Gemini determined the query is irrelevant
    if queries_response.technology == "irrelevant" and queries_response.queries == [
        "irrelevant"
    ]:
        yield event_message(
            "query_not_relevant",
            {
                "message": "This query doesn't appear to be related to technical or coding issues.",
                "reason": "The query seems to be about general knowledge, personal information, or non-technical topics.",
                "suggested_rephrase": "Try asking about programming errors, framework issues, or development problems.",
            },
        )
        return

    yield event_message("search_queries", data=queries_response.model_dump())

    # Get repository name
    if not search_request.repo:
        repo = await get_repository(technology=queries_response.technology)
    else:
        repo_exists = await check_repo_exists(repo=search_request.repo)
        if not repo_exists:
            repo = await get_repository(technology=search_request.repo)
        else:
            repo = search_request.repo

    yield event_message("get_repository", {"repo": repo})

    # Search for issues using Github REST API
    issues = await search_issues(repo=repo, queries=queries_response.queries)
    yield event_message("search_issues", {"total_issues": len(issues)})

    issues_with_comments = await get_issues_with_comments(repo=repo, issues=issues)

    total_comments = sum((len(issue["comments"]) for issue in issues_with_comments))
    yield event_message("get_issues_comments", {"total_comments": total_comments})

    # Use Gemini to generate an answer based on the collected data
    yield event_message(
        "generate_streaming_answer_start",
        {"message": "Generating AI response..."},
    )

    async for payload in generate_streaming_answer(
        request=request,
        user_query=search_request.query,
        issues_with_comments=issues_with_comments,
    ):
        if isinstance(payload, dict):
            kind = payload.get("type")
            data = payload.get("data")
            if kind == "answer":
                yield event_message("streaming_answer_chunk", data)
            elif kind == "sources":
                yield event_message("sources_update", data)
            elif kind == "error":
                yield event_message("streaming_error", {"message": data})
        else:
            # Back-compat: if the generator yields raw text, treat as answer chunk
            yield event_message("streaming_answer_chunk", payload)

    end_time = time.time()
    elapsed_time = end_time - start_time

    yield event_message(
        "streaming_answer_end",
        {
            "message": "Response complete",
            "elapsed_time_seconds": round(elapsed_time, 2),
        },
    )


@router.get("/search")
async def search_get(request: Request, search_request: SearchRequest = Depends()):
    return StreamingResponse(
        search_stream(search_request=search_request, request=request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
