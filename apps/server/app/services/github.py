from githubkit import GitHub
from githubkit.versions.latest.models import IssueSearchResultItem, IssueComment
from ..core.config import settings
from ..exceptions.github_exceptions import handle_github_exceptions

gh = GitHub(settings.GITHUB_TOKEN)


@handle_github_exceptions
async def search_issues(
    *, repo: str, queries: list[str]
) -> list[IssueSearchResultItem]:
    """
    Search for issues in a repository and return them.
    """

    issues = []

    for query in queries:
        resp = await gh.rest.search.async_issues_and_pull_requests(
            q=f"repo:{repo} is:issue {query}",
            order="desc",
            sort="reactions",
        )
        print(f"repo:{repo} is:issue {query}")
        issues.extend(resp.parsed_data.items)

    # Remove duplicate issues
    unique_issues = {}
    for issue in issues:
        if issue.id not in unique_issues:
            unique_issues[issue.id] = issue

    issues = list(unique_issues.values())

    issue_numbers = [issue.number for issue in issues]
    print([f"{issue.number}- {issue.title}" for issue in issues])

    return issues, issue_numbers


async def get_issues_comments(
    *, repo: str, issue_numbers: list[int]
) -> list[IssueComment]:

    username, repo = repo.split("/")

    comments = []

    for issue_num in issue_numbers:
        resp = await gh.rest.issues.async_list_comments(
            owner=username, repo=repo, issue_number=issue_num
        )
        comments.extend(resp.parsed_data)

    return comments


async def get_repository(*, technology: str) -> str:
    """ """
    repo = await gh.rest.search.async_repos(
        q=f"{technology}", sort="stars", order="desc"
    )
    return repo.parsed_data.items[0].full_name
