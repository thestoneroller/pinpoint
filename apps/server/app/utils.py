from fastapi import HTTPException
from .services.github import gh
from .exceptions.github_exceptions import handle_github_exceptions
import json


@handle_github_exceptions
async def check_repo_exists(*, repo: str) -> bool:
    """
    Check if a GitHub repository exists.
    """
    repo_str = repo.strip()
    parts = repo_str.split("/")
    if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
        raise HTTPException(
            status_code=422, detail="Invalid repo format. Expected 'username/repo'."
        )
    username, repo_name = parts[0], parts[1]

    await gh.rest.repos.async_get(owner=username, repo=repo_name)
    return True


def event_message(event_type: str, data: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
