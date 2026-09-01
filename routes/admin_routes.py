from flask import render_template, jsonify, session, request
from app import app

from security.roles import require_role, get_role, ROLE_LEVEL
from services import admin_service
from services.admin_service import AdminError


# ============================================================
# PANEL PAGE
# ============================================================

@app.route("/admin")
@require_role("moderator")
def admin_panel():
    role = get_role(session["username"])
    return render_template("admin.html", role=role)


# ============================================================
# STATS
# ============================================================

@app.route("/admin/api/stats")
@require_role("moderator")
def admin_stats():
    return jsonify({"success": True, "stats": admin_service.platform_stats(),
                     "your_role": get_role(session["username"])})


# ============================================================
# USERS
# ============================================================

@app.route("/admin/api/users")
@require_role("moderator")
def admin_list_users():
    search = request.args.get("search", "").strip() or None
    page = max(1, request.args.get("page", 1, type=int))
    return jsonify({"success": True, **admin_service.list_users(search=search, page=page)})


@app.route("/admin/api/users/<username>")
@require_role("moderator")
def admin_user_detail(username):
    user = admin_service.get_user_detail(username)
    if user is None:
        return jsonify({"success": False, "error": "not_found"}), 404
    return jsonify({"success": True, "user": user})


@app.route("/admin/api/users/created-between")
@require_role("moderator")
def admin_accounts_created_between():
    start = request.args.get("from")
    end = request.args.get("to")
    if not start or not end:
        return jsonify({"success": False, "error": "invalid_input", "detail": "both 'from' and 'to' (YYYY-MM-DD) are required"}), 400
    accounts = admin_service.accounts_created_between(start, end)
    return jsonify({"success": True, "from": start, "to": end, "count": len(accounts), "accounts": accounts})


# ============================================================
# ROLE CHANGES -- owner only (enforced at the route AND service layer)
# ============================================================

@app.route("/admin/api/users/<username>/role", methods=["POST"])
@require_role("owner")
def admin_set_role(username):
    data = request.get_json(silent=True) or {}
    new_role = data.get("role")
    reason = (data.get("reason") or "").strip()

    try:
        admin_service.set_role(session["username"], get_role(session["username"]), username, new_role, reason)
    except AdminError as e:
        return jsonify({"success": False, "error": "action_failed", "detail": str(e)}), 400

    return jsonify({"success": True})


# ============================================================
# SUSPEND / RESTORE -- moderators can act on ordinary users;
# service layer blocks moderators from touching other admins
# ============================================================

@app.route("/admin/api/users/<username>/suspend", methods=["POST"])
@require_role("moderator")
def admin_suspend_user(username):
    data = request.get_json(silent=True) or {}
    reason = (data.get("reason") or "").strip()
    if not reason:
        return jsonify({"success": False, "error": "invalid_input", "detail": "a reason is required"}), 400

    my_role = get_role(session["username"])
    try:
        admin_service.set_suspended(session["username"], my_role, username, True, reason)
    except AdminError as e:
        return jsonify({"success": False, "error": "action_failed", "detail": str(e)}), 403

    return jsonify({"success": True})


@app.route("/admin/api/users/<username>/restore", methods=["POST"])
@require_role("moderator")
def admin_restore_user(username):
    my_role = get_role(session["username"])
    try:
        admin_service.set_suspended(session["username"], my_role, username, False, "restored")
    except AdminError as e:
        return jsonify({"success": False, "error": "action_failed", "detail": str(e)}), 403

    return jsonify({"success": True})


# ============================================================
# LEADERBOARD VISIBILITY -- moderator-level power
# ============================================================

@app.route("/admin/api/users/<username>/leaderboard-visibility", methods=["POST"])
@require_role("moderator")
def admin_set_leaderboard_visibility(username):
    data = request.get_json(silent=True) or {}
    visible = bool(data.get("visible", True))
    reason = (data.get("reason") or "").strip() or None

    my_role = get_role(session["username"])
    try:
        admin_service.set_leaderboard_visibility(session["username"], my_role, username, visible, reason)
    except AdminError as e:
        return jsonify({"success": False, "error": "action_failed", "detail": str(e)}), 400

    return jsonify({"success": True})


# ============================================================
# ECONOMY -- owner only
# ============================================================

@app.route("/admin/api/users/<username>/coins", methods=["POST"])
@require_role("owner")
def admin_adjust_coins(username):
    data = request.get_json(silent=True) or {}
    try:
        amount = int(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "invalid_input", "detail": "amount must be an integer"}), 400
    reason = (data.get("reason") or "").strip()

    try:
        new_balance = admin_service.adjust_coins(session["username"], "owner", username, amount, reason)
    except AdminError as e:
        return jsonify({"success": False, "error": "action_failed", "detail": str(e)}), 400

    return jsonify({"success": True, "new_balance": new_balance})


@app.route("/admin/api/users/<username>/xp", methods=["POST"])
@require_role("owner")
def admin_adjust_xp(username):
    data = request.get_json(silent=True) or {}
    try:
        amount = int(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "invalid_input", "detail": "amount must be an integer"}), 400
    reason = (data.get("reason") or "").strip()

    try:
        updated = admin_service.adjust_xp(session["username"], "owner", username, amount, reason)
    except AdminError as e:
        return jsonify({"success": False, "error": "action_failed", "detail": str(e)}), 400

    return jsonify({"success": True, "level": updated["level"], "xp": updated["xp"]})


# ============================================================
# AUDIT LOG
# ============================================================

@app.route("/admin/api/audit-log")
@require_role("moderator")
def admin_audit_log():
    limit = min(500, request.args.get("limit", 100, type=int))
    # moderators only see their own actions; owners see everything
    my_role = get_role(session["username"])
    filter_to_self = None if my_role == "owner" else session["username"]
    return jsonify({"success": True, "entries": admin_service.get_audit_log(filter_to_self, limit)})
