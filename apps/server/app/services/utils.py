from .github import gh
from ..exceptions.github_exceptions import handle_github_exceptions


@handle_github_exceptions
async def check_repo_exists(*, repo: str) -> bool:
    """
    Check if a GitHub repository exists.
    """
    owner, repo_name = repo.split("/")
    await gh.rest.repos.async_get(owner=owner, repo=repo_name)
    return True
