from fastapi import APIRouter
from ...services.github import search_issues
from ...services.utils import check_repo_exists

router = APIRouter()


@router.post("/search")
async def search(*, repo: str, query: str):
    """Search for issues in a GitHub repository."""

    # Check if repo exists first
    repo_exists = await check_repo_exists(repo=repo)
    if not repo_exists:
        pass

    # Search for issues - exceptions are handled automatically
    issues = await search_issues(repo=repo, query=query)

    return {"repo": repo, "query": query, "issues": issues}
