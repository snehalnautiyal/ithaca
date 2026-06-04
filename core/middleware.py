from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from core.auth import get_user_id_from_cookie
from core.config import settings

PUBLIC_PATHS = {"/login", "/logout", "/health"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.auth_enabled:
            return await call_next(request)

        path = request.url.path
        if path in PUBLIC_PATHS or path.startswith("/static"):
            return await call_next(request)

        if get_user_id_from_cookie(request) is None:
            return RedirectResponse("/login", status_code=302)

        return await call_next(request)
