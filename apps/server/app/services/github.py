from githubkit import GitHub
from githubkit.versions.latest.models import IssueSearchResultItem
from app.core.config import settings

gh = GitHub(settings.GITHUB_TOKEN)


async def search_issues(*, repo: str, query: str) -> list[IssueSearchResultItem]:
    """
    Search for issues in a repository and return them.
    """
    owner, repo_name = repo.split("/")

    resp = await gh.rest.search.async_issues_and_pull_requests(
        q=f"repo:{owner}/{repo_name} is:issue {query}",
        sort="created",
    )

    issues: list[IssueSearchResultItem] = resp.parsed_data.items
    for issue in issues:
        print(f"#{issue.number}: {issue.title}")

    return issues
