from flask import render_template, jsonify, session, request, redirect, url_for
from app import app

from services import multiplayer_service
from services.multiplayer_service import RoomError


def _require_login():
    return "username" in session


@app.route("/multiplayer")
def multiplayer_hub():
    if not _require_login():
        return redirect(url_for("index"))
    from profiles import get_profile
    from services.shop_service import theme_css_classes
    profile = get_profile(session["username"])
    return render_template("multiplayer.html", theme_classes=theme_css_classes(profile.get("profile_theme")))


@app.route("/multiplayer/tic-tac-toe")
def multiplayer_ttt_page():
    if not _require_login():
        return redirect(url_for("index"))
    from profiles import get_profile
    from services.shop_service import theme_css_classes
    profile = get_profile(session["username"])
    return render_template(
        "multiplayer_ttt.html",
        username=session["username"],
        theme_classes=theme_css_classes(profile.get("profile_theme")),
    )


@app.route("/api/multiplayer/create", methods=["POST"])
def mp_create():
    if not _require_login():
        return jsonify({"error": "not_authenticated"}), 401
    data = request.get_json(silent=True) or {}
    game_id = data.get("game_id")
    if game_id != "tic_tac_toe_mp":
        return jsonify({"error": "unsupported_game", "detail": "Only tic_tac_toe_mp exists so far."}), 400
    try:
        code = multiplayer_service.create_room(session["username"], game_id, max_players=2)
    except RoomError as e:
        return jsonify({"error": "room_error", "detail": str(e)}), 400
    return jsonify({"ok": True, "room_code": code})


@app.route("/api/multiplayer/join", methods=["POST"])
def mp_join():
    if not _require_login():
        return jsonify({"error": "not_authenticated"}), 401
    data = request.get_json(silent=True) or {}
    room_code = (data.get("room_code") or "").strip().upper()
    if not room_code:
        return jsonify({"error": "invalid_input", "detail": "room_code is required"}), 400
    try:
        multiplayer_service.join_room(session["username"], room_code)
    except RoomError as e:
        return jsonify({"error": "room_error", "detail": str(e)}), 400
    return jsonify({"ok": True, "room_code": room_code})


@app.route("/api/multiplayer/leave", methods=["POST"])
def mp_leave():
    if not _require_login():
        return jsonify({"error": "not_authenticated"}), 401
    data = request.get_json(silent=True) or {}
    room_code = (data.get("room_code") or "").strip().upper()
    multiplayer_service.leave_room(session["username"], room_code)
    return jsonify({"ok": True})


@app.route("/api/multiplayer/ready", methods=["POST"])
def mp_ready():
    if not _require_login():
        return jsonify({"error": "not_authenticated"}), 401
    data = request.get_json(silent=True) or {}
    room_code = (data.get("room_code") or "").strip().upper()
    ready = bool(data.get("ready", True))
    try:
        multiplayer_service.set_ready(session["username"], room_code, ready)
    except RoomError as e:
        return jsonify({"error": "room_error", "detail": str(e)}), 400
    return jsonify({"ok": True})


@app.route("/api/multiplayer/room/<room_code>")
def mp_room_state(room_code):
    if not _require_login():
        return jsonify({"error": "not_authenticated"}), 401
    try:
        state = multiplayer_service.get_room(room_code.upper(), session["username"])
    except RoomError as e:
        return jsonify({"error": "room_error", "detail": str(e)}), 404
    return jsonify({"ok": True, **state})


@app.route("/api/multiplayer/move", methods=["POST"])
def mp_move():
    if not _require_login():
        return jsonify({"error": "not_authenticated"}), 401
    data = request.get_json(silent=True) or {}
    room_code = (data.get("room_code") or "").strip().upper()
    move = data.get("move") or {}
    if not room_code or not isinstance(move, dict):
        return jsonify({"error": "invalid_input"}), 400
    try:
        new_state = multiplayer_service.apply_move(session["username"], room_code, move)
    except RoomError as e:
        return jsonify({"error": "room_error", "detail": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": "invalid_move", "detail": str(e)}), 400
    return jsonify({"ok": True, "state": new_state})
