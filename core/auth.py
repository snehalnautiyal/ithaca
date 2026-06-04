import hashlib
import hmac
import secrets
import time
from typing import Optional

import bcrypt
from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from core.config import settings
from core.database import User

router = APIRouter()

COOKIE_NAME = "ithaca_session"
COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _sign(value: str) -> str:
    sig = hmac.new(settings.secret_key.encode(), value.encode(), hashlib.sha256).hexdigest()
    return f"{value}.{sig}"


def _unsign(signed: str) -> Optional[str]:
    if "." not in signed:
        return None
    value, sig = signed.rsplit(".", 1)
    expected = hmac.new(settings.secret_key.encode(), value.encode(), hashlib.sha256).hexdigest()
    if hmac.compare_digest(sig, expected):
        return value
    return None


def make_session_cookie(user_id: int) -> str:
    return _sign(f"{user_id}:{int(time.time())}")


def get_user_id_from_cookie(request: Request) -> Optional[int]:
    raw = request.cookies.get(COOKIE_NAME)
    if not raw:
        return None
    value = _unsign(raw)
    if not value:
        return None
    try:
        uid, _ = value.split(":", 1)
        return int(uid)
    except (ValueError, AttributeError):
        return None


def ensure_admin(db: Session) -> None:
    if db.query(User).count() == 0:
        password = secrets.token_urlsafe(12)
        user = User(
            username="admin",
            hashed_password=hash_password(password),
            is_admin=True,
        )
        db.add(user)
        db.commit()
        print("\n" + "=" * 50)
        print("  Ithaca — First boot")
        print(f"  Admin username : admin")
        print(f"  Admin password : {password}")
        print("  Save this — it won't be shown again.")
        print("=" * 50 + "\n")


_LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ithaca — Login</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0f0f0f;color:#e0e0e0;font-family:system-ui,sans-serif;
     display:flex;align-items:center;justify-content:center;min-height:100vh}}
.card{{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:2.5rem;width:100%;max-width:360px}}
h1{{font-size:1.6rem;font-weight:700;color:#7c6af7;margin-bottom:1.5rem;text-align:center}}
label{{display:block;font-size:.85rem;color:#aaa;margin-bottom:.3rem}}
input{{width:100%;background:#0f0f0f;border:1px solid #333;border-radius:8px;
      color:#e0e0e0;padding:.65rem .9rem;font-size:.95rem;outline:none;margin-bottom:1rem}}
input:focus{{border-color:#7c6af7}}
button{{width:100%;background:#7c6af7;color:#fff;border:none;border-radius:8px;
        padding:.75rem;font-size:1rem;cursor:pointer;font-weight:600}}
button:hover{{background:#6a59e0}}
.err{{color:#f87171;font-size:.85rem;margin-bottom:.8rem;text-align:center}}
</style>
</head>
<body>
<div class="card">
  <h1>◈ Ithaca</h1>
  {error}
  <form method="post" action="/login">
    <label>Username</label>
    <input name="username" type="text" autocomplete="username" required autofocus>
    <label>Password</label>
    <input name="password" type="password" autocomplete="current-password" required>
    <button type="submit">Sign in</button>
  </form>
</div>
</body>
</html>"""


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    if get_user_id_from_cookie(request):
        return RedirectResponse("/", status_code=302)
    return HTMLResponse(_LOGIN_HTML.format(error=""))


@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    from core.database import SessionLocal
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            html = _LOGIN_HTML.format(error='<p class="err">Invalid username or password.</p>')
            return HTMLResponse(html, status_code=401)
        cookie_val = make_session_cookie(user.id)
        resp = RedirectResponse("/", status_code=302)
        resp.set_cookie(COOKIE_NAME, cookie_val, max_age=COOKIE_MAX_AGE, httponly=True, samesite="lax")
        return resp
    finally:
        db.close()


@router.post("/logout")
async def logout():
    resp = RedirectResponse("/login", status_code=302)
    resp.delete_cookie(COOKIE_NAME)
    return resp
