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

    username, repo = repo.split("/")
    issues = []

    for query in queries:
        resp = await gh.rest.search.async_issues_and_pull_requests(
            q=f"repo:{username}/{repo} is:issue {query} ",
            order="desc",
            sort="reactions",
        )
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
    """ """
    username, repo = repo.split("/")

    repo_comments = await gh.rest.issues.async_list_comments_for_repo(
        owner=username, repo=repo
    )

    issue_base_url = f"https://api.github.com/repos/{username}/{repo}/issues/"
    target_issue_urls = {f"{issue_base_url}{issue_num}" for issue_num in issue_numbers}

    issue_comments = [
        comment
        for comment in repo_comments.parsed_data
        if comment.issue_url in target_issue_urls
    ]

    return issue_comments


async def get_repository(*, technology: str) -> str:
    """ """
    repo = await gh.rest.search.async_repos(
        q=f"{technology}", sort="stars", order="desc"
    )
    return repo.parsed_data.items[0].full_name
