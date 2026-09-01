from flask import request, jsonify, session
from app import app

from services.economy_service import (
    start_game_session,
    grant_game_reward,
    DuplicateResultError,
    UnknownGameError,
    InvalidSessionError,
)


@app.route("/api/games/start", methods=["POST"])
def start_game():
    """Called when a game actually begins. Issues a server-side session
    token that report-result later has to present -- the client never
    gets to invent its own."""
    if "username" not in session:
        return jsonify({"error": "not_authenticated"}), 401

    data = request.get_json(silent=True) or {}
    game_id = data.get("game_id")
    if not isinstance(game_id, str) or not game_id:
        return jsonify({"error": "invalid_input", "detail": "game_id must be a non-empty string"}), 400

    try:
        token = start_game_session(session["username"], game_id)
    except UnknownGameError as e:
        return jsonify({"error": "unknown_game", "detail": str(e)}), 400

    return jsonify({"ok": True, "session_token": token})


@app.route("/api/games/report-result", methods=["POST"])
def report_game_result():
    """Called when a game ends. Requires the session_token from
    /api/games/start -- the server decides what it's worth, and won't
    pay out a session twice or before it's been open long enough for
    the claimed tier."""
    if "username" not in session:
        return jsonify({"error": "not_authenticated"}), 401

    data = request.get_json(silent=True) or {}
    game_id = data.get("game_id")
    tier = data.get("tier")
    session_token = data.get("session_token")

    if not all(isinstance(v, str) and v for v in (game_id, tier, session_token)):
        return jsonify({"error": "invalid_input", "detail": "game_id, tier, and session_token must all be non-empty strings"}), 400

    try:
        result = grant_game_reward(
            username=session["username"],
            game_id=game_id,
            tier=tier,
            session_token=session_token,
        )
    except DuplicateResultError as e:
        return jsonify({"error": "duplicate_result", "detail": str(e)}), 409
    except InvalidSessionError as e:
        return jsonify({"error": "invalid_session", "detail": str(e)}), 403
    except UnknownGameError as e:
        return jsonify({"error": "unknown_game_or_tier", "detail": str(e)}), 400

    return jsonify({"ok": True, **result})
