import logging
from functools import wraps
from fastapi import HTTPException

def handle_exceptions(status_code=500, error_prefix="Error"):
    """
    Decorator to wrap FastAPI endpoint handlers with consistent exception handling.
    
    Args:
        status_code: HTTP status code to return on exception (default: 500)
        error_prefix: Text prefix for the error message (default: "Error")
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logging.exception(f"{error_prefix}")
                raise HTTPException(
                    status_code=status_code, 
                    detail=f"{error_prefix}: {str(e)}"
                )
        return wrapper
    return decorator