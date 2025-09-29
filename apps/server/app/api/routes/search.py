import time

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from ...models import SearchRequest
from ...services.gemini import generate_issue_queries, generate_streaming_answer
from ...services.github import get_issues_with_comments, get_repository, search_issues
from ...utils import check_repo_exists, event_message

router = APIRouter()


async def search_stream(search_request: SearchRequest, request: Request):
    """Search for issues in a GitHub repository."""

    start_time = time.time()

    # Send SSE preamble to defeat proxy buffering and signal stream open
    # The long comment chunk helps some proxies (and serverless providers) start streaming immediately
    yield ":" + (" " * 1024) + "\n\n"
    yield event_message("ready", {"message": "stream open"})

    # Use Gemini to generate 3 queries to search in Github Issues
    try:
        queries_response = await generate_issue_queries(
            request=request, user_query=search_request.query
        )
    except HTTPException as he:
        # Emit a streaming error event and stop the stream
        yield event_message("streaming_error", {"message": he.detail})
        return
    except Exception:
        yield event_message(
            "streaming_error", {"message": "Failed to generate search queries."}
        )
        return

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

    # Determine repository with safe fallback
    if not search_request.repo:
        repo = await get_repository(technology=queries_response.technology)
    else:
        try:
            await check_repo_exists(repo=search_request.repo)
            repo = search_request.repo
        except HTTPException as he:
            # For invalid/non-existent repo (404/422), fall back to auto-selection
            if he.status_code in (404, 422):
                # Inform client we are falling back
                yield event_message("repo_invalid", {"provided": search_request.repo})
                repo = await get_repository(technology=queries_response.technology)
            else:
                # For other errors (auth/rate-limit), notify client and stop
                yield event_message("streaming_error", {"message": he.detail})
                return

    # If still no repository could be determined, stop nicely
    if not repo:
        yield event_message(
            "streaming_error",
            {"message": "No suitable repository found for this query."},
        )
        return

    yield event_message("get_repository", {"repo": repo})

    # Search for issues using Github REST API
    try:
        issues = await search_issues(repo=repo, queries=queries_response.queries)
    except HTTPException as he:
        yield event_message("streaming_error", {"message": he.detail})
        return
    except Exception:
        yield event_message("streaming_error", {"message": "Failed to search issues."})
        return

    yield event_message("search_issues", {"total_issues": len(issues)})

    # Get comments
    try:
        issues_with_comments = await get_issues_with_comments(repo=repo, issues=issues)
    except HTTPException as he:
        yield event_message("streaming_error", {"message": he.detail})
        return
    except Exception:
        yield event_message(
            "streaming_error", {"message": "Failed to fetch issue comments."}
        )
        return

    total_comments = sum((len(issue["comments"]) for issue in issues_with_comments))
    yield event_message("get_issues_comments", {"total_comments": total_comments})

    # Use Gemini to generate an answer based on the collected data
    yield event_message(
        "generate_streaming_answer_start",
        {"message": "Generating AI response..."},
    )

    try:
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
                yield event_message("streaming_answer_chunk", payload)
    except HTTPException as he:
        yield event_message("streaming_error", {"message": he.detail})
        return
    except Exception:
        yield event_message(
            "streaming_error", {"message": "Failed to generate AI answer."}
        )
        return

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
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
