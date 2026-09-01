"""
Shared multiplayer room infrastructure -- create/join/ready/leave, plus
a generic state_json blob per room. Every multiplayer game (Tic-Tac-Toe
first, then the rest) uses this same room lifecycle instead of each
game inventing its own; only the actual move-validation logic differs
per game (see services/multiplayer_games/).

No WebSockets in this sandbox (no network access to install
Flask-SocketIO), so this is polling-based: the client asks
"what's the room state right now" every ~1.5s. That's a real,
working pattern for turn-based games -- it's not as instant as a
socket push, but it's not fake either.
"""

import json
import random
import string
from datetime import datetime

from security.database import get_connection, ensure_db


class RoomError(Exception):
    pass


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _generate_room_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=5))


def create_room(username, game_id, max_players=2):
    ensure_db()
    conn = get_connection()
    try:
        for _ in range(10):
            code = _generate_room_code()
            exists = conn.execute(
                "SELECT 1 FROM multiplayer_rooms WHERE room_code = ?", (code,)
            ).fetchone()
            if not exists:
                break
        else:
            raise RoomError("couldn't generate a free room code, try again")

        now = _now()
        cur = conn.execute(
            """INSERT INTO multiplayer_rooms
               (room_code, game_id, host_username, status, max_players, state_json, created_at, updated_at)
               VALUES (?, ?, ?, 'waiting', ?, '{}', ?, ?)""",
            (code, game_id, username, max_players, now, now),
        )
        room_id = cur.lastrowid
        conn.execute(
            "INSERT INTO multiplayer_players (room_id, username, seat, ready, connected, joined_at) "
            "VALUES (?, ?, 0, 0, 1, ?)",
            (room_id, username, now),
        )
        conn.commit()
        return code
    finally:
        conn.close()


def join_room(username, room_code):
    ensure_db()
    conn = get_connection()
    try:
        room = conn.execute(
            "SELECT * FROM multiplayer_rooms WHERE room_code = ?", (room_code,)
        ).fetchone()
        if room is None:
            raise RoomError("no room with that code")
        if room["status"] != "waiting":
            raise RoomError("that room has already started or finished")

        existing = conn.execute(
            "SELECT seat FROM multiplayer_players WHERE room_id = ? AND username = ?",
            (room["id"], username),
        ).fetchone()
        if existing is not None:
            return room_code  # already in this room -- idempotent, not an error

        players = conn.execute(
            "SELECT seat FROM multiplayer_players WHERE room_id = ? ORDER BY seat",
            (room["id"],),
        ).fetchall()
        if len(players) >= room["max_players"]:
            raise RoomError("room is full")

        next_seat = len(players)
        conn.execute(
            "INSERT INTO multiplayer_players (room_id, username, seat, ready, connected, joined_at) "
            "VALUES (?, ?, ?, 0, 1, ?)",
            (room["id"], username, next_seat, _now()),
        )
        conn.commit()
        return room_code
    finally:
        conn.close()


def leave_room(username, room_code):
    ensure_db()
    conn = get_connection()
    try:
        room = conn.execute(
            "SELECT * FROM multiplayer_rooms WHERE room_code = ?", (room_code,)
        ).fetchone()
        if room is None:
            return
        conn.execute(
            "UPDATE multiplayer_players SET connected = 0 WHERE room_id = ? AND username = ?",
            (room["id"], username),
        )
        remaining = conn.execute(
            "SELECT COUNT(*) c FROM multiplayer_players WHERE room_id = ? AND connected = 1",
            (room["id"],),
        ).fetchone()["c"]
        if remaining == 0:
            conn.execute(
                "UPDATE multiplayer_rooms SET status = 'finished', updated_at = ? WHERE id = ?",
                (_now(), room["id"]),
            )
        conn.commit()
    finally:
        conn.close()


def set_ready(username, room_code, ready):
    ensure_db()
    conn = get_connection()
    try:
        room = conn.execute(
            "SELECT * FROM multiplayer_rooms WHERE room_code = ?", (room_code,)
        ).fetchone()
        if room is None:
            raise RoomError("no room with that code")

        conn.execute(
            "UPDATE multiplayer_players SET ready = ? WHERE room_id = ? AND username = ?",
            (1 if ready else 0, room["id"], username),
        )
        conn.commit()

        # auto-start once the room is full and everyone's ready
        players = conn.execute(
            "SELECT username, ready FROM multiplayer_players WHERE room_id = ? AND connected = 1",
            (room["id"],),
        ).fetchall()
        if room["status"] == "waiting" and len(players) == room["max_players"] and all(p["ready"] for p in players):
            _start_room(conn, room)
        conn.commit()
    finally:
        conn.close()


def _start_room(conn, room):
    from services.multiplayer_games import get_game_module
    game = get_game_module(room["game_id"])
    players = conn.execute(
        "SELECT username FROM multiplayer_players WHERE room_id = ? ORDER BY seat",
        (room["id"],),
    ).fetchall()
    initial_state = game.initial_state([p["username"] for p in players])
    conn.execute(
        "UPDATE multiplayer_rooms SET status = 'active', state_json = ?, updated_at = ? WHERE id = ?",
        (json.dumps(initial_state), _now(), room["id"]),
    )


def get_room(room_code, username):
    """Full room state for polling. Raises if this user isn't a participant --
    room state (including the board) is only visible to people actually in it."""
    ensure_db()
    conn = get_connection()
    try:
        room = conn.execute(
            "SELECT * FROM multiplayer_rooms WHERE room_code = ?", (room_code,)
        ).fetchone()
        if room is None:
            raise RoomError("no room with that code")

        players = conn.execute(
            "SELECT username, seat, ready, connected FROM multiplayer_players "
            "WHERE room_id = ? ORDER BY seat",
            (room["id"],),
        ).fetchall()
        if not any(p["username"] == username for p in players):
            raise RoomError("you're not in this room")

        return {
            "room_code": room["room_code"],
            "game_id": room["game_id"],
            "status": room["status"],
            "host": room["host_username"],
            "max_players": room["max_players"],
            "state": json.loads(room["state_json"]),
            "players": [dict(p) for p in players],
        }
    finally:
        conn.close()


def apply_move(username, room_code, move):
    """Delegates the actual move validation/application to the specific
    game's module -- this function only owns the room lifecycle (is it
    this room, is it active, whose turn is it structurally) and reward
    payout once the game module says it's over."""
    from services.multiplayer_games import get_game_module
    from services.economy_service import grant_game_reward, DuplicateResultError

    ensure_db()
    conn = get_connection()
    try:
        room = conn.execute(
            "SELECT * FROM multiplayer_rooms WHERE room_code = ?", (room_code,)
        ).fetchone()
        if room is None:
            raise RoomError("no room with that code")
        if room["status"] != "active":
            raise RoomError("this room isn't active")

        players = conn.execute(
            "SELECT username, seat FROM multiplayer_players WHERE room_id = ? ORDER BY seat",
            (room["id"],),
        ).fetchall()
        if not any(p["username"] == username for p in players):
            raise RoomError("you're not in this room")

        game = get_game_module(room["game_id"])
        state = json.loads(room["state_json"])
        new_state = game.apply_move(state, username, move, [dict(p) for p in players])

        status = "active"
        if new_state.get("game_over"):
            status = "finished"

        conn.execute(
            "UPDATE multiplayer_rooms SET state_json = ?, status = ?, updated_at = ? WHERE id = ?",
            (json.dumps(new_state), status, _now(), room["id"]),
        )
        conn.commit()

        if status == "finished" and not new_state.get("rewards_granted"):
            _grant_match_rewards(conn, room, new_state, [dict(p) for p in players])

        return new_state
    finally:
        conn.close()


def _grant_match_rewards(conn, room, state, players):
    from services.economy_service import grant_multiplayer_reward, DuplicateResultError

    tiers = state.get("reward_tiers", {})
    for p in players:
        tier = tiers.get(p["username"])
        if not tier:
            continue
        token = f"mp-{room['room_code']}-{p['username']}"
        try:
            grant_multiplayer_reward(p["username"], "generic_multiplayer", tier, token)
        except DuplicateResultError:
            pass  # already paid out -- fine, idempotent
        except Exception:
            pass  # don't let a reward hiccup break the match result itself

    state["rewards_granted"] = True
    conn.execute(
        "UPDATE multiplayer_rooms SET state_json = ? WHERE id = ?",
        (json.dumps(state), room["id"]),
    )
    conn.commit()
