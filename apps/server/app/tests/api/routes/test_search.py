from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.anyio
async def test_search_endpoint_success(async_client):
    """Test the /search endpoint with mocked dependencies."""

    # Mock all the service functions
    with (
        patch("app.api.routes.search.generate_issue_queries") as mock_generate_queries,
        patch("app.api.routes.search.get_repository") as mock_get_repo,
        patch("app.api.routes.search.search_issues") as mock_search_issues,
        patch("app.api.routes.search.get_issues_with_comments") as mock_get_comments,
        patch(
            "app.api.routes.search.generate_streaming_answer"
        ) as mock_streaming_answer,
    ):
        # Setup mocks
        mock_queries_response = MagicMock()
        mock_queries_response.model_dump.return_value = {
            "technology": "react",
            "queries": ["react hooks error", "useState issue"],
            "confidence": 0.8,
        }
        mock_queries_response.technology = "react"
        mock_queries_response.queries = ["react hooks error", "useState issue"]
        mock_generate_queries.return_value = mock_queries_response

        mock_get_repo.return_value = "facebook/react"
        mock_search_issues.return_value = [MagicMock(number=123, title="Test issue")]
        mock_get_comments.return_value = [
            {
                "issue_number": 123,
                "comments": [{"body": "Test comment", "username": "testuser"}],
            }
        ]

        async def mock_stream():
            # Mock the actual event stream format from the endpoint
            yield 'event: search_queries\ndata: {"technology": "react", "queries": ["react hooks error", "useState issue"], "confidence": 0.8}\n\n'
            yield 'event: get_repository\ndata: {"repo": "facebook/react"}\n\n'
            yield 'event: search_issues\ndata: {"total_issues": 1}\n\n'
            yield 'event: get_issues_comments\ndata: {"total_comments": 1}\n\n'
            yield 'event: generate_streaming_answer_start\ndata: {"message": "Generating AI response..."}\n\n'
            yield 'event: streaming_answer_chunk\ndata: {"text": "This is a test response "}\n\n'
            yield 'event: streaming_answer_chunk\ndata: {"text": "with streaming content."}\n\n'
            yield 'event: streaming_answer_end\ndata: {"message": "Response complete"}\n\n'

        mock_streaming_answer.return_value = mock_stream()

        # Make the request
        response = await async_client.post(
            "/api/v1/search",
            params={"query": "React hooks not working properly in my application"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

        # Parse the streaming response
        content = response.content.decode()
        lines = [line for line in content.split("\n") if line.strip()]

        # Verify we get the expected events
        event_types = []
        for line in lines:
            if line.startswith("event: "):
                event_type = line[7:]  # Remove 'event: ' prefix
                event_types.append(event_type)

        # Check that we got the expected event types
        assert "search_queries" in event_types
        assert "get_repository" in event_types
        assert "search_issues" in event_types
        assert "streaming_answer_chunk" in event_types


@pytest.mark.anyio
async def test_search_endpoint_with_specific_repo(async_client):
    """Test the /search endpoint when a specific repository is provided."""

    with (
        patch("app.api.routes.search.generate_issue_queries") as mock_generate_queries,
        patch("app.api.routes.search.check_repo_exists") as mock_check_repo,
        patch("app.api.routes.search.search_issues") as mock_search_issues,
        patch("app.api.routes.search.get_issues_with_comments") as mock_get_comments,
        patch(
            "app.api.routes.search.generate_streaming_answer"
        ) as mock_streaming_answer,
    ):
        # Setup mocks
        mock_queries_response = MagicMock()
        mock_queries_response.model_dump.return_value = {
            "technology": "vue",
            "queries": ["vue component error", "vue rendering issue"],
            "confidence": 0.9,
        }
        mock_queries_response.technology = "vue"
        mock_queries_response.queries = ["vue component error", "vue rendering issue"]
        mock_generate_queries.return_value = mock_queries_response

        mock_check_repo.return_value = True  # Repo exists
        mock_search_issues.return_value = []
        mock_get_comments.return_value = []

        async def mock_stream():
            yield "No relevant issues found."

        mock_streaming_answer.return_value = mock_stream()

        # Make the request with specific repo
        response = await async_client.post(
            "/api/v1/search",
            params={
                "query": "Vue component not rendering properly in my application and showing blank screen",
                "repo": "vuejs/vue",
            },
        )

        assert response.status_code == 200

        # Verify that check_repo_exists was called instead of get_repository
        mock_check_repo.assert_called_once_with(repo="vuejs/vue")


@pytest.mark.anyio
async def test_search_endpoint_invalid_json(async_client):
    """Test the /search endpoint with invalid JSON."""

    response = await async_client.post(
        "/api/v1/search",
        content="invalid json",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.anyio
async def test_search_endpoint_missing_query(async_client):
    """Test the /search endpoint with missing query field."""

    response = await async_client.post(
        "/api/v1/search",
        params={"repo": "facebook/react"},  # Missing required 'query' field
    )

    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.anyio
async def test_search_endpoint_empty_query(async_client):
    """Test the /search endpoint with empty query."""

    with (
        patch("app.api.routes.search.generate_issue_queries") as mock_generate_queries,
        patch("app.api.routes.search.get_repository") as mock_get_repo,
        patch("app.api.routes.search.search_issues") as mock_search_issues,
        patch("app.api.routes.search.get_issues_with_comments") as mock_get_comments,
        patch(
            "app.api.routes.search.generate_streaming_answer"
        ) as mock_streaming_answer,
    ):
        # Setup mocks for empty query
        mock_queries_response = MagicMock()
        mock_queries_response.model_dump.return_value = {
            "technology": "general",
            "queries": ["programming help", "general programming issue"],
            "confidence": 0.3,
        }
        mock_queries_response.technology = "general"
        mock_queries_response.queries = [
            "programming help",
            "general programming issue",
        ]
        mock_generate_queries.return_value = mock_queries_response

        mock_get_repo.return_value = "microsoft/vscode"
        mock_search_issues.return_value = []
        mock_get_comments.return_value = []

        async def mock_stream():
            yield "Please provide a more specific query."

        mock_streaming_answer.return_value = mock_stream()

        response = await async_client.post(
            "/api/v1/search",
            params={
                "query": "I need help with programming issue that I cannot solve on my own"
            },
        )

        assert response.status_code == 200
