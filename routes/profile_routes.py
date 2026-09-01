from flask import render_template, session, redirect, url_for, jsonify, request
from app import app
from services.profile_service import get_profile
from services.shop_service import theme_css_classes, get_user_inventory, get_item
from profiles import avatar_url, banner_url, get_default_profile


def _leaderboard_rank(profile):
    from security.database import get_connection, ensure_db
    ensure_db()
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT COUNT(*) + 1 AS rank FROM users
               WHERE leaderboard_visible = 1
                 AND (level > ? OR (level = ? AND xp > ?))""",
            (profile["level"], profile["level"], profile["xp"]),
        ).fetchone()
        return row["rank"]
    finally:
        conn.close()


def _grouped_inventory(username):
    """Owned items grouped by category, each with its full item data and
    whether it's currently equipped -- built once here so the profile
    page and any future page can reuse it instead of re-deriving it."""
    from profiles import get_profile as _get_profile

    owned = get_user_inventory(username)
    profile = _get_profile(username)
    equipped_ids = {
        profile.get("avatar"),
        profile.get("profile_banner"),
        profile.get("profile_theme"),
    }

    grouped = {"avatars": [], "banners": [], "themes": []}
    for row in owned:
        item = get_item(row["item_id"])
        if item is None:
            continue
        item = dict(item)
        item["equipped"] = item["id"] in equipped_ids
        grouped.setdefault(item["category"], []).append(item)
    return grouped


def _render_profile(target_username, viewer_username):
    profile = get_profile(target_username)
    if profile is None:
        return None

    xp_needed = profile["level"] * 100
    xp_percent = round(min(100, (profile["xp"] / xp_needed) * 100), 1) if xp_needed else 0
    is_own = (viewer_username == target_username)

    return render_template(
        "profile.html",
        profile=profile,
        avatar_src=avatar_url(profile),
        banner_src=banner_url(profile),
        xp_percent=xp_percent,
        theme_classes=theme_css_classes(profile.get("profile_theme")) if is_own else "",
        rank=_leaderboard_rank(profile),
        inventory=_grouped_inventory(target_username),
        is_own_profile=is_own,
    )


@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("index"))
    return _render_profile(session["username"], session["username"])


@app.route("/profile/<username>")
def view_profile(username):
    username = username.lower()
    if "username" not in session:
        return redirect(url_for("index"))
    if username == session["username"]:
        return redirect(url_for("profile"))
    page = _render_profile(username, session["username"])
    if page is None:
        return redirect(url_for("hub"))
    return page


@app.route("/api/profile/bio", methods=["POST"])
def update_bio():
    """The real endpoint the old page's Save button was missing --
    it was previously calling /api/save_profile, which never existed."""
    if "username" not in session:
        return jsonify({"success": False, "error": "not_authenticated"}), 401

    data = request.get_json(silent=True) or {}
    bio = (data.get("bio") or "").strip()
    if len(bio) > 300:
        return jsonify({"success": False, "error": "invalid_input", "detail": "Bio must be 300 characters or fewer."}), 400

    from profiles import update_profile
    update_profile(session["username"], biography=bio)
    return jsonify({"success": True, "biography": bio})


@app.route("/leaderboard")
def leaderboard():
    from security.database import get_connection, ensure_db

    ensure_db()
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT username, uid, level, xp, coins, avatar, avatar_type,
                   games_played, games_won
            FROM users
            WHERE leaderboard_visible = 1
            ORDER BY level DESC, xp DESC, username ASC
            LIMIT 100
            """
        ).fetchall()
    finally:
        conn.close()

    entries = []
    for i, row in enumerate(rows, start=1):
        entry = dict(row)
        entry["rank"] = i
        entry["avatar_src"] = avatar_url(entry)
        entries.append(entry)

    current_user = session.get("username")

    # Leaderboard always uses its own fixed charcoal/silver design,
    # not the viewer's purchased theme -- same as the login page.
    return render_template(
        "leaderboard.html",
        entries=entries,
        current_user=current_user,
    )


@app.route("/settings")
def settings():
    return "Settings (Coming Soon)"


@app.route("/achievements")
def achievements():
    return "Achievements (Coming Soon)"