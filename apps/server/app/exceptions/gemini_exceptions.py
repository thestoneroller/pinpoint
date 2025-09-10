from functools import wraps
from typing import TypeVar
import inspect

from fastapi import HTTPException

from google.genai import errors as genai_errors

R = TypeVar("R")


def handle_gemini_exceptions(func):
    """
    Decorator to handle Gemini exceptions.
    """

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            _handle_exception(e)

    @wraps(func)
    async def async_generator_wrapper(*args, **kwargs):
        try:
            async for item in func(*args, **kwargs):
                yield item
        except Exception as e:
            _handle_exception(e)

    # Check if the function is an async generator
    if inspect.isasyncgenfunction(func):
        return async_generator_wrapper
    else:
        return async_wrapper


def _handle_exception(e: Exception) -> None:
    """Handle exceptions and convert them to appropriate HTTPExceptions."""

    if genai_errors and isinstance(e, genai_errors.APIError):
        return _handle_genai_api_error(e)

    # Handle google.genai.errors.ServerError if available
    if (
        genai_errors
        and hasattr(genai_errors, "ServerError")
        and isinstance(e, genai_errors.ServerError)
    ):
        raise HTTPException(status_code=500, detail="Gemini server error occurred")

    # Handle function-related errors from google.genai
    if (
        genai_errors
        and hasattr(genai_errors, "UnknownFunctionCallArgumentError")
        and isinstance(e, genai_errors.UnknownFunctionCallArgumentError)
    ):
        raise HTTPException(
            status_code=422, detail=f"Function call argument error: {str(e)}"
        )

    if (
        genai_errors
        and hasattr(genai_errors, "UnsupportedFunctionError")
        and isinstance(e, genai_errors.UnsupportedFunctionError)
    ):
        raise HTTPException(status_code=400, detail=f"Unsupported function: {str(e)}")

    if (
        genai_errors
        and hasattr(genai_errors, "FunctionInvocationError")
        and isinstance(e, genai_errors.FunctionInvocationError)
    ):
        raise HTTPException(
            status_code=422, detail=f"Function invocation failed: {str(e)}"
        )

    if (
        genai_errors
        and hasattr(genai_errors, "UnknownApiResponseError")
        and isinstance(e, genai_errors.UnknownApiResponseError)
    ):
        raise HTTPException(status_code=502, detail="Unable to parse API response")

    # Handle instructor validation errors
    if isinstance(e, ValueError):
        error_msg = str(e).lower()
        if "validation" in error_msg or "pydantic" in error_msg:
            raise HTTPException(
                status_code=422, detail=f"Response validation failed: {str(e)}"
            )
        elif "model" in error_msg and (
            "not found" in error_msg or "invalid" in error_msg
        ):
            raise HTTPException(
                status_code=404, detail=f"Invalid model configuration: {str(e)}"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")

    # Handle network connectivity issues
    if isinstance(e, ConnectionError):
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to Gemini service. Please check your connection.",
            headers={"Retry-After": "60"},
        )

    # Handle request timeouts
    if isinstance(e, TimeoutError):
        raise HTTPException(
            status_code=504,
            detail="Request timed out while waiting for Gemini response",
            headers={"Retry-After": "30"},
        )

    # Check for common error patterns in the message for generic exceptions
    error_msg = str(e).lower()

    if "rate limit" in error_msg or "quota" in error_msg:
        raise HTTPException(
            status_code=429,
            detail="Rate limit or quota exceeded",
            headers={"Retry-After": "60"},
        )
    elif "timeout" in error_msg or "deadline" in error_msg:
        raise HTTPException(
            status_code=504, detail="Request timed out", headers={"Retry-After": "30"}
        )
    elif (
        "permission" in error_msg
        or "unauthorized" in error_msg
        or "api key" in error_msg
    ):
        raise HTTPException(
            status_code=403, detail="Access denied. Check API key and permissions."
        )
    elif "not found" in error_msg or "404" in error_msg:
        raise HTTPException(status_code=404, detail="Resource not found")
    elif "blocked" in error_msg or "safety" in error_msg:
        raise HTTPException(
            status_code=400, detail="Content was blocked due to safety settings"
        )
    elif "recitation" in error_msg:
        raise HTTPException(
            status_code=400,
            detail="Content blocked due to recitation concerns. Try making your prompt more unique.",
        )
    else:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error in Gemini service: {str(e)}"
        )


def _handle_genai_api_error(e) -> None:
    """Handle google.genai.errors.APIError based on status code."""
    status_code = getattr(e, "code", 500)
    message = getattr(e, "message", str(e))

    if status_code == 400:
        raise HTTPException(status_code=400, detail=f"Invalid request: {message}")
    elif status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid or expired API key")
    elif status_code == 403:
        raise HTTPException(status_code=403, detail="Access denied or quota exceeded")
    elif status_code == 404:
        raise HTTPException(status_code=404, detail="Model or resource not found")
    elif status_code == 429:
        raise HTTPException(
            status_code=429, detail="Rate limit exceeded", headers={"Retry-After": "60"}
        )
    elif status_code == 500:
        raise HTTPException(status_code=500, detail="Internal server error")
    elif status_code == 503:
        raise HTTPException(
            status_code=503,
            detail="Service unavailable",
            headers={"Retry-After": "120"},
        )
    else:
        # Fallback for unknown status codes
        raise HTTPException(
            status_code=status_code if 400 <= status_code <= 599 else 500,
            detail=f"Gemini API error: {message}",
        )
