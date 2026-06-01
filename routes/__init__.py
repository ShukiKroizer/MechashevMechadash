from functools import wraps
from datetime import datetime, timezone
from flask import session, redirect, url_for

_SESSION_MAX_AGE = 8 * 3600  # 8 hours in seconds


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("auth.login"))
        login_at = session.get("login_at")
        if login_at is None or (datetime.now(timezone.utc).timestamp() - login_at) > _SESSION_MAX_AGE:
            session.clear()
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated
