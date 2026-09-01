"""
Admin panel business logic.

Every mutating function logs to admin_audit_log: who, what, to whom,
before/after state, and why (spec section 53). Nothing in this file
can ever grant 'owner' -- see security/roles.py for why that's
deliberate. Moderators get read access plus low-risk moderation
actions (suspend/restore ordinary users, hide from leaderboard);
owners additionally get economy control (coins/XP) and role changes.
"""

import json
from datetime import datetime

from security.database import get_connection, ensure_db


class AdminError(Exception):
    pass


def _log(conn, admin_username, admin_role, action, target_type, target_id,
         previous_state, new_state, reason):
    conn.execute(
        """INSERT INTO admin_audit_log
           (admin_username, admin_role, action, target_type, target_id,
            previous_state, new_state, reason, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            admin_username, admin_role, action, target_type,
            str(target_id) if target_id is not None else None,
            json.dumps(previous_state) if previous_state is not None else None,
            json.dumps(new_state) if new_state is not None else None,
            reason,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )


# ==========================================
# USERS
# ==========================================

def list_users(search=None, page=1, per_page=25):
    ensure_db()
    conn = get_connection()
    try:
        offset = (page - 1) * per_page
        cols = ("username, uid, role, level, xp, coins, suspended, "
                "leaderboard_visible, account_creation_date, last_online")
        if search:
            like = f"%{search}%"
            rows = conn.execute(
                f"SELECT {cols} FROM users WHERE username LIKE ? OR uid LIKE ? "
                f"ORDER BY account_creation_date DESC LIMIT ? OFFSET ?",
                (like, like, per_page, offset),
            ).fetchall()
            total = conn.execute(
                "SELECT COUNT(*) c FROM users WHERE username LIKE ? OR uid LIKE ?", (like, like)
            ).fetchone()["c"]
        else:
            rows = conn.execute(
                f"SELECT {cols} FROM users ORDER BY account_creation_date DESC LIMIT ? OFFSET ?",
                (per_page, offset),
            ).fetchall()
            total = conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
        return {"users": [dict(r) for r in rows], "total": total, "page": page, "per_page": per_page}
    finally:
        conn.close()


def get_user_detail(username):
    ensure_db()
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if row is None:
            return None
        user = dict(row)
        user.pop("password_hash", None)
        user["achievements"] = json.loads(user.get("achievements") or "[]")
        user["badges"] = json.loads(user.get("badges") or "[]")

        inventory = conn.execute(
            "SELECT item_id, acquired_at FROM user_inventory WHERE username = ?", (username,)
        ).fetchall()
        user["inventory"] = [dict(r) for r in inventory]

        recent_tx = conn.execute(
            "SELECT type, amount, balance_after, source, related_item, created_at "
            "FROM coin_transactions WHERE username = ? ORDER BY id DESC LIMIT 20",
            (username,),
        ).fetchall()
        user["recent_transactions"] = [dict(r) for r in recent_tx]

        return user
    finally:
        conn.close()


def accounts_created_between(start_date, end_date):
    """start_date / end_date: 'YYYY-MM-DD' strings, inclusive."""
    ensure_db()
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT username, uid, account_creation_date, role
               FROM users
               WHERE date(account_creation_date) BETWEEN date(?) AND date(?)
               ORDER BY account_creation_date ASC""",
            (start_date, end_date),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ==========================================
# ROLES -- owner only, and 'owner' is never a settable value here
# ==========================================

def set_role(admin_username, admin_role, target_username, new_role, reason):
    if new_role not in ("user", "moderator"):
        raise AdminError("this can only set 'user' or 'moderator' -- owner isn't grantable here")
    if admin_role != "owner":
        raise AdminError("only an owner can change roles")
    if target_username == admin_username:
        raise AdminError("can't change your own role")

    ensure_db()
    conn = get_connection()
    try:
        row = conn.execute("SELECT role FROM users WHERE username = ?", (target_username,)).fetchone()
        if row is None:
            raise AdminError("no such user")
        if row["role"] == "owner":
            raise AdminError("owner role can't be changed through the admin panel")

        conn.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, target_username))
        _log(conn, admin_username, admin_role, "SET_ROLE", "user", target_username,
             {"role": row["role"]}, {"role": new_role}, reason)
        conn.commit()
    finally:
        conn.close()


# ==========================================
# SUSPEND / RESTORE -- moderators can act on ordinary users only
# ==========================================

def set_suspended(admin_username, admin_role, target_username, suspended, reason):
    if target_username == admin_username:
        raise AdminError("can't suspend your own account")

    ensure_db()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT role, suspended FROM users WHERE username = ?", (target_username,)
        ).fetchone()
        if row is None:
            raise AdminError("no such user")
        if row["role"] in ("moderator", "owner") and admin_role != "owner":
            raise AdminError("moderators can't suspend other admins")

        conn.execute(
            "UPDATE users SET suspended = ?, suspend_reason = ? WHERE username = ?",
            (1 if suspended else 0, reason if suspended else None, target_username),
        )
        _log(conn, admin_username, admin_role, "SUSPEND" if suspended else "RESTORE",
             "user", target_username, {"suspended": bool(row["suspended"])},
             {"suspended": bool(suspended)}, reason)
        conn.commit()
    finally:
        conn.close()


# ==========================================
# LEADERBOARD VISIBILITY -- available to moderators too
# ==========================================

def set_leaderboard_visibility(admin_username, admin_role, target_username, visible, reason):
    ensure_db()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT leaderboard_visible FROM users WHERE username = ?", (target_username,)
        ).fetchone()
        if row is None:
            raise AdminError("no such user")
        conn.execute(
            "UPDATE users SET leaderboard_visible = ? WHERE username = ?",
            (1 if visible else 0, target_username),
        )
        _log(conn, admin_username, admin_role, "SET_LEADERBOARD_VISIBILITY", "user", target_username,
             {"leaderboard_visible": bool(row["leaderboard_visible"])},
             {"leaderboard_visible": bool(visible)}, reason)
        conn.commit()
    finally:
        conn.close()


# ==========================================
# ECONOMY -- owner only, reason required both times
# ==========================================

def adjust_coins(admin_username, admin_role, target_username, amount, reason):
    if admin_role != "owner":
        raise AdminError("only an owner can adjust coins directly")
    if not reason or not reason.strip():
        raise AdminError("a reason is required for balance adjustments")
    if amount == 0:
        raise AdminError("amount can't be zero")

    from profiles import get_profile, save_profile
    ensure_db()
    conn = get_connection()
    try:
        profile = get_profile(target_username)
        if profile is None:
            raise AdminError("no such user")
        before = profile["coins"]
        profile["coins"] = max(0, before + amount)
        save_profile(target_username, profile)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            """INSERT INTO coin_transactions
               (username, type, amount, balance_before, balance_after, source, related_item, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (target_username, "ADMIN_GRANT" if amount >= 0 else "ADMIN_DEDUCTION",
             amount, before, profile["coins"], admin_username, None, now),
        )
        _log(conn, admin_username, admin_role, "ADJUST_COINS", "user", target_username,
             {"coins": before}, {"coins": profile["coins"]}, reason)
        conn.commit()
        return profile["coins"]
    finally:
        conn.close()


def adjust_xp(admin_username, admin_role, target_username, amount, reason):
    if admin_role != "owner":
        raise AdminError("only an owner can adjust XP directly")
    if not reason or not reason.strip():
        raise AdminError("a reason is required for XP adjustments")
    if amount == 0:
        raise AdminError("amount can't be zero")

    from profiles import get_profile, add_xp
    ensure_db()
    conn = get_connection()
    try:
        profile = get_profile(target_username)
        if profile is None:
            raise AdminError("no such user")
        before = {"level": profile["level"], "xp": profile["xp"]}
        updated = add_xp(target_username, amount)
        _log(conn, admin_username, admin_role, "ADJUST_XP", "user", target_username,
             before, {"level": updated["level"], "xp": updated["xp"]}, reason)
        conn.commit()
        return updated
    finally:
        conn.close()


# ==========================================
# AUDIT LOG / STATS
# ==========================================

def get_audit_log(admin_username_filter=None, limit=100):
    ensure_db()
    conn = get_connection()
    try:
        if admin_username_filter:
            rows = conn.execute(
                "SELECT * FROM admin_audit_log WHERE admin_username = ? ORDER BY id DESC LIMIT ?",
                (admin_username_filter, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM admin_audit_log ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def platform_stats():
    ensure_db()
    conn = get_connection()
    try:
        return {
            "total_users": conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"],
            "total_suspended": conn.execute("SELECT COUNT(*) c FROM users WHERE suspended=1").fetchone()["c"],
            "total_moderators": conn.execute("SELECT COUNT(*) c FROM users WHERE role='moderator'").fetchone()["c"],
            "total_coins_in_circulation": conn.execute("SELECT COALESCE(SUM(coins),0) s FROM users").fetchone()["s"],
            "total_purchases": conn.execute("SELECT COUNT(*) c FROM user_inventory").fetchone()["c"],
            "total_game_results": conn.execute("SELECT COUNT(*) c FROM game_results").fetchone()["c"],
        }
    finally:
        conn.close()
