import os
import uvicorn

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.responses import RedirectResponse

from app.api.api import api_router
from app.settings import settings


DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

WHITELISTED_TOKEN = os.getenv("WHITELISTED_TOKEN")

security = HTTPBearer()


async def verify_token(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> str:
    """
    Verify that the provided token matches the whitelisted token.

    Args:
        credentials: The HTTP authorization credentials containing the bearer token

    Returns:
        The validated token

    Raises:
        HTTPException: If token is invalid or not configured
    """
    if not WHITELISTED_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication not configured",
        )

    if credentials.credentials != WHITELISTED_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials


app = FastAPI(title="Transfermarkt API")
app.state.limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMITING_FREQUENCY],
    enabled=settings.RATE_LIMITING_ENABLE,
)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.include_router(api_router, dependencies=[Depends(verify_token)])


@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=DEBUG)
