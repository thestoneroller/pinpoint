from unittest.mock import AsyncMock, MagicMock, patch


import pytest
from app.services.github import get_issues_with_comments, get_repository, search_issues

"""Unit tests for GitHub service functions."""


@pytest.mark.anyio
async def test_search_issues_success():
    """Test successful issue search."""
    # Create mock IssueSearchResultItem-like objects with attributes
    mock_issue = MagicMock()
    mock_issue.id = 1
    mock_issue.number = 123
    mock_issue.title = "Test issue"
    mock_issue.html_url = "https://github.com/owner/repo/issues/123"
    mock_issue.body = "Test body"
    mock_issue.state = "open"

    with patch("app.services.github.gh") as mock_gh:
        mock_gh.rest.search.async_issues_and_pull_requests = AsyncMock(
            return_value=MagicMock(parsed_data=MagicMock(items=[mock_issue]))
        )

        result = await search_issues(repo="owner/repo", queries=["test query"])

        assert len(result) == 1
        assert result[0].number == 123
        assert result[0].title == "Test issue"


@pytest.mark.anyio
async def test_search_issues_empty_result():
    """Test search with no results."""
    with patch("app.services.github.gh") as mock_gh:
        mock_gh.rest.search.async_issues_and_pull_requests = AsyncMock(
            return_value=MagicMock(parsed_data=MagicMock(items=[]))
        )

        result = await search_issues(repo="owner/repo", queries=["nonexistent query"])

        assert result == []


@pytest.mark.anyio
async def test_get_issues_with_comments():
    """Test fetching issues with comments."""
    # Create mock IssueSearchResultItem-like input
    mock_issue = MagicMock()
    mock_issue.id = 1
    mock_issue.number = 123
    mock_issue.title = "Test issue"
    mock_issue.html_url = "https://github.com/owner/repo/issues/123"
    mock_issue.body = "Issue body"
    issues = [mock_issue]

    # Create mock comment objects with expected attributes
    mock_comment = MagicMock()
    mock_comment.body = "Test comment"
    mock_comment.user = MagicMock(login="testuser")
    mock_comment.html_url = "https://github.com/owner/repo/issues/123#issuecomment-1"
    mock_comment.reactions = MagicMock(total_count=5)

    with patch("app.services.github.gh") as mock_gh:
        mock_gh.rest.issues.async_list_comments = AsyncMock(
            return_value=MagicMock(parsed_data=[mock_comment])
        )

        result = await get_issues_with_comments(repo="owner/repo", issues=issues)

        assert len(result) == 1
        assert result[0]["issue_number"] == 123
        assert len(result[0]["comments"]) == 1
        assert result[0]["comments"][0]["body"] == "Test comment"
        assert result[0]["comments"][0]["username"] == "testuser"


@pytest.mark.anyio
async def test_get_repository_success():
    """Test successful repository search."""
    with patch("app.services.github.gh") as mock_gh:
        mock_repo_item = MagicMock(full_name="facebook/react")
        mock_gh.rest.search.async_repos = AsyncMock(
            return_value=MagicMock(parsed_data=MagicMock(items=[mock_repo_item]))
        )

        result = await get_repository(technology="react")

        assert result == "facebook/react"


@pytest.mark.anyio
async def test_get_repository_no_results():
    """Test repository search with no results."""
    with patch("app.services.github.gh") as mock_gh:
        mock_gh.rest.search.async_repos = AsyncMock(
            return_value=MagicMock(parsed_data=MagicMock(items=[]))
        )

        result = await get_repository(technology="nonexistent")

        assert result is None
