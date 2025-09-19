import asyncio

from githubkit import GitHub
from githubkit.versions.latest.models import IssueSearchResultItem

from ..core.config import settings
from ..exceptions.github_exceptions import handle_github_exceptions
from ..models import CommentData, IssueWithComments

gh = GitHub(settings.GITHUB_TOKEN)


@handle_github_exceptions
async def search_issues(
    *, repo: str, queries: list[str]
) -> list[IssueSearchResultItem]:
    """
    Search for issues in a repository and return them.
    """

    issue_tasks = []

    # Wrap individual API calls so failures don't bubble up and break the TaskGroup
    async def _search_single(query: str):
        try:
            return await gh.rest.search.async_issues_and_pull_requests(
                q=f"repo:{repo} is:issue {query}", order="desc", sort="reactions"
            )
        except Exception:
            return None

    async with asyncio.TaskGroup() as tg:
        for query in queries:
            task = tg.create_task(_search_single(query))
            issue_tasks.append(task)

    issues = []
    unique_issues = {}

    for task in issue_tasks:
        response = task.result()
        if response is None:
            continue
        issues.extend(response.parsed_data.items)

    for issue in issues:
        if issue.id not in unique_issues:
            unique_issues[issue.id] = issue

    unique_issues = list(unique_issues.values())

    return unique_issues


@handle_github_exceptions
async def get_issues_with_comments(
    *,
    repo: str,
    issues: list[IssueSearchResultItem],
    max_comments_per_issue: int = 5,
    max_total_comments: int = 100,
) -> list[IssueWithComments]:
    """
    Get comments for each issue and return the ones with the most reactions.
    """

    if not issues:
        return []

    username, repo_name = repo.split("/")

    issue_map = {issue.number: issue for issue in issues}
    issue_numbers = [issue.number for issue in issues]

    # To calculate how many issues to process to stay within total limit so we don't exceed Gemini's 250K TPM Limit
    max_issues = min(len(issue_numbers), max_total_comments // max_comments_per_issue)

    # Wrap comment fetch so failures don't bubble up and break the TaskGroup
    async def _fetch_comments(issue_num: int):
        try:
            return await gh.rest.issues.async_list_comments(
                owner=username,
                repo=repo_name,
                issue_number=issue_num,
                page=1,
                per_page=100,
            )
        except Exception:
            return None

    comment_tasks = []

    async with asyncio.TaskGroup() as tg:
        for issue_num in issue_numbers[:max_issues]:
            task = tg.create_task(_fetch_comments(issue_num))
            comment_tasks.append((issue_num, task))

    def get_reaction_count(comment) -> int:
        if not (hasattr(comment, "reactions") and comment.reactions):
            return 0
        return getattr(comment.reactions, "total_count", 0) or 0

    issues_with_comments: list[IssueWithComments] = []

    for issue_num, task in comment_tasks:
        issue = issue_map[issue_num]
        response = task.result()
        if response is None:
            # Skip issues whose comments couldn't be fetched
            continue
        issue_comments = response.parsed_data

        # Sort by reaction count and take top comments for this issue
        sorted_comments = sorted(issue_comments, key=get_reaction_count, reverse=True)
        top_comments = sorted_comments[:max_comments_per_issue]

        batched_comments: list[CommentData] = [
            {
                "body": c.body or "",
                "username": c.user.login if c.user else "unknown",
                "comment_url": c.html_url,
            }
            for c in top_comments
        ]

        issues_with_comments.append(
            {
                "issue_number": issue.number,
                "title": issue.title,
                "issue_url": issue.html_url,
                "body": issue.body or "No description provided.",
                "comments": batched_comments,
            }
        )

    return issues_with_comments


async def get_repository(*, technology: str) -> str | None:
    """ """
    repo = await gh.rest.search.async_repos(
        q=f"{technology}", sort="stars", order="desc"
    )
    items = getattr(repo.parsed_data, "items", None) or []
    if not items:
        return None
    return items[0].full_name
