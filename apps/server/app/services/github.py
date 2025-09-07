import asyncio
from githubkit import GitHub
from githubkit.versions.latest.models import IssueSearchResultItem
from ..models import CommentData, IssueWithComments
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

    print([f"{issue.number}- {issue.title}" for issue in unique_issues])

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

    comment_tasks = []

    async with asyncio.TaskGroup() as tg:
        for issue_num in issue_numbers[:max_issues]:
            task = tg.create_task(
                gh.rest.issues.async_list_comments(
                    owner=username,
                    repo=repo_name,
                    issue_number=issue_num,
                    page=1,
                    per_page=100,
                )
            )
            comment_tasks.append((issue_num, task))

    def get_reaction_count(comment) -> int:
        if not (hasattr(comment, "reactions") and comment.reactions):
            return 0
        return getattr(comment.reactions, "total_count", 0) or 0

    issues_with_comments: list[IssueWithComments] = []

    for issue_num, task in comment_tasks:
        issue = issue_map[issue_num]
        response = task.result()
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

    print("Top Comments: ", issues_with_comments[:1])
    return issues_with_comments


async def get_repository(*, technology: str) -> str:
    """ """
    repo = await gh.rest.search.async_repos(
        q=f"{technology}", sort="stars", order="desc"
    )
    return repo.parsed_data.items[0].full_name
