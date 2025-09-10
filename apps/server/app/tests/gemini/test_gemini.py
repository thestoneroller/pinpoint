from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import Request

from app.services.gemini import generate_issue_queries, generate_streaming_answer


"""Unit tests for Gemini service functions."""


@pytest.mark.anyio
async def test_generate_issue_queries_success():
    """Test successful query generation."""
    mock_request = MagicMock(spec=Request)
    mock_llm = AsyncMock()
    mock_request.state.llm = mock_llm

    # Mock the expected response structure
    mock_response = MagicMock()
    mock_response.technology = "shadcn"
    mock_response.queries = [
        "table header fixed",
        "scrollable table body",
        "fixed header table",
    ]
    mock_response.confidence = 0.8

    mock_llm.messages.create.return_value = mock_response

    result = await generate_issue_queries(
        request=mock_request,
        user_query="how to make shadcn table header fixed to the top and table body scrollable",
    )

    assert result.technology == "shadcn"
    assert len(result.queries) == 3
    assert "table header fixed" in result.queries
    assert "scrollable table body" in result.queries
    assert "fixed header table" in result.queries
    assert result.confidence == 0.8
    mock_llm.messages.create.assert_called_once()


@pytest.mark.anyio
async def test_generate_streaming_answer_success():
    """Test successful streaming answer generation."""
    mock_request = MagicMock(spec=Request)
    mock_llm = AsyncMock()
    mock_request.state.llm = mock_llm

    # Mock streaming response
    async def mock_stream():
        yield "To make a table header fixed and the body scrollable, "
        yield "you can utilize CSS positioning and a scrollable container. "
        yield "Here are approaches based on the provided information:\n\n"
        yield "## Solution 1: Using `ScrollArea` and `sticky` positioning\n\n"
        yield "This method involves wrapping your `Table` component with `ScrollArea` "
        yield "and applying `sticky top-0` to the `TableHeader`."

    mock_llm.messages.create.return_value = mock_stream()

    mock_issues = [
        {
            "number": 1234,
            "title": "Table header not sticky in ScrollArea",
            "comments": [
                {
                    "body": "Use sticky top-0 class on TableHeader",
                    "author": "shadcn-expert",
                }
            ],
        }
    ]

    chunks = []
    async for chunk in generate_streaming_answer(
        request=mock_request,
        user_query="how to make shadcn table header fixed to the top and table body scrollable",
        issues_with_comments=mock_issues,
    ):
        chunks.append(chunk)

    assert len(chunks) == 6
    assert "ScrollArea" in "".join(chunks)
    assert "sticky" in "".join(chunks)
    mock_llm.messages.create.assert_called_once()


@pytest.mark.anyio
async def test_generate_issue_queries_with_empty_query():
    """Test query generation with empty user query."""
    mock_request = MagicMock(spec=Request)
    mock_llm = AsyncMock()
    mock_request.state.llm = mock_llm

    mock_response = MagicMock()
    mock_response.technology = "general"
    mock_response.queries = ["programming help", "coding issue", "software problem"]
    mock_response.confidence = 0.3

    mock_llm.messages.create.return_value = mock_response

    result = await generate_issue_queries(request=mock_request, user_query="")

    assert result.technology == "general"
    assert len(result.queries) == 3
    assert result.confidence == 0.3


@pytest.mark.anyio
async def test_generate_issue_queries_high_confidence():
    """Test query generation with high confidence technology detection."""
    mock_request = MagicMock(spec=Request)
    mock_llm = AsyncMock()
    mock_request.state.llm = mock_llm

    mock_response = MagicMock()
    mock_response.technology = "react"
    mock_response.queries = [
        "react hooks error",
        "useState issue",
        "useEffect problem",
    ]
    mock_response.confidence = 0.95
    mock_response.model_dump.return_value = {
        "technology": "react",
        "queries": ["react hooks error", "useState issue", "useEffect problem"],
        "confidence": 0.95,
    }

    mock_llm.messages.create.return_value = mock_response

    result = await generate_issue_queries(
        request=mock_request,
        user_query="React hooks not working properly in my component",
    )

    assert result.technology == "react"
    assert result.confidence == 0.95
    assert all(
        "react" in query.lower() or "use" in query.lower() for query in result.queries
    )


@pytest.mark.anyio
async def test_generate_streaming_answer_with_code_examples():
    """Test streaming answer that includes code examples."""
    mock_request = MagicMock(spec=Request)
    mock_llm = AsyncMock()
    mock_request.state.llm = mock_llm

    async def mock_stream_with_code():
        yield "```tsx\n"
        yield '<TableHeader className="sticky top-0 bg-secondary">\n'
        yield "  {/* Table header content */}\n"
        yield "</TableHeader>\n"
        yield "```"

    mock_llm.messages.create.return_value = mock_stream_with_code()

    mock_issues = [
        {
            "number": 567,
            "title": "How to make table header sticky",
            "comments": [{"body": "Add sticky top-0 class", "author": "developer"}],
        }
    ]

    chunks = []
    async for chunk in generate_streaming_answer(
        request=mock_request,
        user_query="show me code for sticky table header",
        issues_with_comments=mock_issues,
    ):
        chunks.append(chunk)

    full_response = "".join(chunks)
    assert "```tsx" in full_response
    assert "TableHeader" in full_response
    assert "sticky top-0" in full_response
