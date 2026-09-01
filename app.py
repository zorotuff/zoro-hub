import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request, session
from werkzeug.exceptions import HTTPException
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY


# ==========================================
# LOGGING -- so a batch-tested bug leaves a trail
# ==========================================
# Full tracebacks always go to logs/zoro_hub.log (and the console),
# regardless of debug mode. debug=False (the safe default) still hides
# stack traces from whoever's actually using the site -- but nothing is
# ever silently swallowed. When something breaks, check that file first.

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

_file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "zoro_hub.log"), maxBytes=1_000_000, backupCount=3
)
_file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

logging.basicConfig(level=logging.INFO, handlers=[_file_handler, logging.StreamHandler()])
logger = logging.getLogger("zoro_hub")


@app.before_request
def _log_request():
    who = session.get("username", "anonymous")
    logger.info(f"{request.method} {request.path} user={who}")


@app.before_request
def _enforce_suspension():
    """A suspension takes effect immediately, not just on next login --
    checked once per request rather than trusting whatever the session
    said when they logged in."""
    username = session.get("username")
    if not username or request.path.startswith("/static/"):
        return
    from security.database import get_connection, ensure_db
    ensure_db()
    conn = get_connection()
    row = conn.execute("SELECT suspended FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if row and row["suspended"]:
        session.clear()
        if request.path.startswith("/api/") or request.path.startswith("/admin/api/"):
            return {"error": "account_suspended"}, 403
        return redirect(url_for("index"))


@app.errorhandler(Exception)
def _handle_unexpected_error(e):
    if isinstance(e, HTTPException):
        return e  # normal 404s, redirects, aborts -- pass through untouched
    logger.exception(f"UNHANDLED ERROR on {request.method} {request.path}")
    if request.path.startswith("/api/"):
        return {"error": "server_error", "detail": "Something went wrong -- see logs/zoro_hub.log"}, 500
    return "Something went wrong on our end. Check logs/zoro_hub.log for details.", 500


# ==========================================
# IMPORT ROUTES
# ==========================================

from routes.auth_routes import *
from routes.hub_routes import *
from routes.ttt_routes import *
from routes.profile_routes import *
from routes.api_routes import *
from routes.game_routes import *
from routes.admin_routes import *
from routes.multiplayer_routes import *
from services.profile_service import get_profile
from services.shop_service import SHOP_ITEMS

from routes.shop_route import shop_bp

if "zoro_shop" not in app.blueprints:
    app.register_blueprint(shop_bp)

logger.info(f"Zoro Hub ready. Blueprints: {list(app.blueprints.keys())}")


# ============================================================
# OWNER RECOVERY -- a real CLI command, not a web route.
# Run from your own terminal with direct access to the server/database:
#     flask --app app set-owner-password
# It only ever touches an EXISTING account and only ever sets it to
# 'owner' if it wasn't already an admin -- it can't be triggered over
# HTTP, can't be discovered by a normal user, and doesn't add a new
# self-promotion path. This is how you get back into /admin with a
# password you actually know.
# ============================================================

@app.cli.command("set-owner-password")
def set_owner_password():
    import getpass
    from security.database import get_connection, ensure_db
    from security.auth import hash_password

    ensure_db()
    username = input("Username to make/confirm as owner (e.g. zoro): ").strip().lower()

    conn = get_connection()
    try:
        row = conn.execute("SELECT role FROM users WHERE username = ?", (username,)).fetchone()
        if row is None:
            print(f"No account named '{username}' exists yet -- register it in the app first, then rerun this.")
            return

        password = getpass.getpass("New password for this account: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords didn't match -- nothing changed.")
            return
        if len(password) < 8:
            print("Use at least 8 characters -- nothing changed.")
            return

        conn.execute(
            "UPDATE users SET password_hash = ?, role = 'owner', is_admin = 1 WHERE username = ?",
            (hash_password(password), username),
        )
        conn.commit()
        print(f"Done -- '{username}' now has the new password and owner role. Log in normally at /.")
    finally:
        conn.close()

if __name__ == "__main__":

    app.run(
        debug=os.environ.get("FLASK_DEBUG") == "1"
    )