from functools import wraps
from typing import Awaitable, Callable, TypeVar

from fastapi import HTTPException
from githubkit.exception import RateLimitExceeded, RequestFailed, RequestTimeout

R = TypeVar("R")


def handle_github_exceptions(
    func: Callable[..., Awaitable[R]],
) -> Callable[..., Awaitable[R]]:
    """
    Decorator to handle GitHub exceptions.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs) -> R:
        try:
            return await func(*args, **kwargs)
        except RequestFailed as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Resource not found")
            elif e.response.status_code == 403:
                raise HTTPException(
                    status_code=403, detail="Access denied or API rate limit exceeded"
                )
            elif e.response.status_code == 401:
                raise HTTPException(
                    status_code=401, detail="Invalid or expired GitHub token"
                )
            else:
                raise HTTPException(
                    status_code=500, detail=f"GitHub API error: {str(e)}"
                )
        except RateLimitExceeded as e:
            raise HTTPException(
                status_code=429,
                detail="GitHub API rate limit exceeded",
                headers={"Retry-After": str(int(e.retry_after.total_seconds()))},
            )
        except RequestTimeout:
            raise HTTPException(
                status_code=504,
                detail="GitHub API request timed out",
                headers={"Retry-After": "60"},
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    return wrapper
