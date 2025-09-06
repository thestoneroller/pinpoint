import asyncio
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

    issue_tasks = []

    async with asyncio.TaskGroup() as tg:
        for query in queries:
            issue_task = tg.create_task(
                gh.rest.search.async_issues_and_pull_requests(
                    q=f"repo:{repo} is:issue {query}",
                    order="desc",
                    sort="reactions",
                )
            )
            issue_tasks.append(issue_task)

    issues = []
    unique_issues = {}

    for task in issue_tasks:
        response = task.result()
        issues.extend(response.parsed_data.items)

    for issue in issues:
        if issue.id not in unique_issues:
            unique_issues[issue.id] = issue

    unique_issues = list(unique_issues.values())

    issue_numbers = [issue.number for issue in unique_issues]
    print([f"{issue.number}- {issue.title}" for issue in unique_issues])

    return unique_issues, issue_numbers


async def get_issues_comments(
    *, repo: str, issue_numbers: list[int]
) -> list[IssueComment]:

    username, repo = repo.split("/")

    comment_tasks = []

    async with asyncio.TaskGroup() as tg:
        for issue_num in issue_numbers:
            fetch_comments_task = tg.create_task(
                gh.rest.issues.async_list_comments(
                    owner=username, repo=repo, issue_number=issue_num
                )
            )
            comment_tasks.append(fetch_comments_task)

    # Flatten the comments from all responses
    comments = []
    for task in comment_tasks:
        response = task.result()
        comments.extend(response.parsed_data)

    return comments


async def get_repository(*, technology: str) -> str:
    """ """
    repo = await gh.rest.search.async_repos(
        q=f"{technology}", sort="stars", order="desc"
    )
    return repo.parsed_data.items[0].full_name
