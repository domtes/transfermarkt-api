import logging
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.responses import RedirectResponse

from app.api.api import api_router
from app.settings import settings

logger = logging.getLogger(__name__)


if not settings.WHITELISTED_TOKEN:
    logger.warning("WHITELISTED_TOKEN environment variable is not set. API authentication will not work.")

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
    if not settings.WHITELISTED_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication not configured",
        )

    if credentials.credentials != settings.WHITELISTED_TOKEN:
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
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
