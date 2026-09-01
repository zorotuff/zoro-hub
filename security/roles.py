"""
Role hierarchy for the admin panel.

    user (0)  <  moderator (1)  <  owner (2)

Moderator ("small admin") gets moderation powers -- view users, search,
suspend/restore ordinary users, hide accounts from the leaderboard,
view reports and the audit log. They do NOT get economic powers
(granting coins/XP) or the ability to touch other admins' roles.

Owner gets everything, including economy adjustments and promoting/
demoting moderators. Owner status itself is never grantable through
any route in this file, on purpose -- the only way to become an
owner is a direct database change (see _bootstrap_owner in
security/database.py). That keeps the most powerful role off the
web-reachable attack surface entirely, even for an existing owner
whose session gets compromised.
"""

from functools import wraps
from flask import session, jsonify, redirect, url_for

ROLE_LEVEL = {"user": 0, "moderator": 1, "owner": 2}


def get_role(username):
    from security.database import get_connection, ensure_db
    ensure_db()
    conn = get_connection()
    try:
        row = conn.execute("SELECT role FROM users WHERE username = ?", (username,)).fetchone()
        return row["role"] if row else "user"
    finally:
        conn.close()


def require_role(min_role):
    """
    Route decorator. Re-checks the role from the DATABASE on every
    request -- never trusts anything cached in the session -- so a
    demotion takes effect on the very next request, not just the next
    login.
    """
    min_level = ROLE_LEVEL[min_role]

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            username = session.get("username")
            if not username:
                if _wants_json():
                    return jsonify({"error": "not_authenticated"}), 401
                return redirect(url_for("index"))

            role = get_role(username)
            if ROLE_LEVEL.get(role, 0) < min_level:
                if _wants_json():
                    return jsonify({"error": "forbidden", "detail": f"requires {min_role} or higher"}), 403
                return redirect(url_for("hub"))

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def _wants_json():
    from flask import request
    return request.path.startswith("/admin/api/")
