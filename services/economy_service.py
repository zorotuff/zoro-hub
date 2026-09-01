"""
Real reward-granting engine for Zoro Hub.

Reward flow is now two calls, not one:

  1. start_game_session(username, game_id) -> session_token
     Called when a game actually begins. Issued and recorded server-side
     -- the client never invents its own token.

  2. grant_game_reward(username, game_id, tier, session_token)
     Called when the game ends. Requires the session_token from step 1:
       - must exist, belong to this user, match this game_id
       - must not have been redeemed already (one reward per session)
       - must satisfy a minimum elapsed-time floor that scales with the
         claimed tier, so "exceptional" can't be claimed half a second
         after "start"

This does NOT fully re-simulate gameplay server-side (these games run
client-side, and doing real server-side verification of arbitrary game
logic is a much bigger, game-by-game project). What it does do: close
off the trivial abuse path -- calling the API directly in a loop with
fresh tokens and a fake high tier -- which is what the original
client-supplied-token design from last pass was still open to. Treat
this as "meaningfully harder to farm," not "cheat-proof."

No route or client is allowed to set coins/XP directly -- this is the
only path allowed to change them as a result of gameplay.
"""

import random
import secrets
from datetime import datetime

from security.database import get_connection, ensure_db
from profiles import get_profile, save_profile, add_xp


class DuplicateResultError(Exception):
    """Raised when a session_token has already been redeemed."""


class UnknownGameError(Exception):
    pass


class InvalidSessionError(Exception):
    """Raised when a session_token is missing, belongs to someone else,
    doesn't match the claimed game, or hasn't been open long enough for
    the claimed tier."""


# Reward curves taken directly from the Zoro Hub economy spec.
# Each tier maps to (coins_min, coins_max, xp_min, xp_max), ordered
# low -> high (the ordering also drives the minimum-time-per-tier check
# below, since dicts preserve insertion order).
REWARD_CURVES = {
    "kitty": {
        "low": (50, 150, 40, 100),
        "good": (200, 500, 120, 250),
        "high": (600, 1200, 300, 600),
        "exceptional": (1500, 2500, 700, 1000),
    },
    "space_shooter": {
        "low": (100, 250, 75, 150),
        "good": (400, 900, 200, 400),
        "high": (1000, 2500, 500, 900),
        "very_high": (3000, 5000, 1000, 1500),
        "exceptional": (6000, 10000, 1600, 2500),
    },
    "geometry": {
        "normal": (150, 400, 100, 250),
        "hard": (500, 1200, 300, 600),
        "very_hard": (1500, 3500, 700, 1300),
    },
    "horror": {
        "partial": (100, 300, 75, 200),
        "major": (400, 1000, 250, 500),
        "full": (1500, 3000, 700, 1200),
        "exceptional": (3500, 5000, 1300, 2000),
    },
    "chess": {
        "easy_win": (500, 900, 300, 500),
        "medium_win": (1000, 1800, 600, 900),
        "hard_win": (2000, 3500, 1000, 1500),
    },
    "scribble": {
        "participation": (200, 300, 100, 150),
        "third": (500, 800, 250, 400),
        "second": (900, 1300, 450, 650),
        "first": (1500, 2500, 700, 1000),
    },
    "snake_arena": {
        "participation": (200, 300, 100, 150),
        "top3": (600, 1000, 300, 500),
        "second": (1200, 1800, 600, 900),
        "first": (2000, 3000, 1000, 1400),
    },
    # Connect Four, multiplayer Tic-Tac-Toe, Reaction Battle, Mini Race, etc.
    "generic_multiplayer": {
        "participation": (200, 400, 100, 150),
        "good": (500, 1000, 250, 450),
        "top": (1000, 2000, 500, 900),
        "winner": (1500, 3000, 700, 1300),
    },
}

# tic_tac_toe / connect_four / reaction_battle / mini_race don't have their
# own spec'd curves yet (the spec covers them under "other multiplayer"),
# so each currently aliases the generic_multiplayer tiers. Give them a real
# curve of their own once each is actually rebuilt as real multiplayer.
for _alias in ("tic_tac_toe", "connect_four", "reaction_battle", "mini_race"):
    REWARD_CURVES[_alias] = REWARD_CURVES["generic_multiplayer"]

_NON_WIN_TIERS = {"participation", "partial", "low"}

# Minimum seconds a session must have been open before a tier at that
# rank can be claimed. Index 0 = the lowest tier in each curve. Beyond
# the list length, the last value repeats. These are deliberately
# conservative first-pass numbers -- tune per game once real playtesting
# data exists.
MIN_SECONDS_BY_TIER_RANK = [3, 12, 25, 45, 70]

OMNIVERA_COINS = 200_000
OMNIVERA_XP = 50_000  # spec said "substantial XP" without a number -- tune freely
OMNIVERA_MIN_SECONDS = 120  # Omnivera doesn't exist yet as a real game; revisit once it does


def _min_seconds_for(game_id, tier):
    if game_id == "omnivera":
        return OMNIVERA_MIN_SECONDS
    tiers = list(REWARD_CURVES[game_id].keys())
    rank = tiers.index(tier)
    idx = min(rank, len(MIN_SECONDS_BY_TIER_RANK) - 1)
    return MIN_SECONDS_BY_TIER_RANK[idx]


def start_game_session(username, game_id):
    """Called when a game begins. Returns a fresh, server-issued token."""
    ensure_db()
    if game_id != "omnivera" and game_id not in REWARD_CURVES:
        raise UnknownGameError(game_id)

    conn = get_connection()
    try:
        token = secrets.token_urlsafe(24)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO game_sessions (session_token, username, game_id, started_at, used) "
            "VALUES (?, ?, ?, ?, 0)",
            (token, username, game_id, now),
        )
        conn.commit()
        return token
    finally:
        conn.close()


def grant_multiplayer_reward(username, game_id, tier, result_token):
    """
    Reward path for multiplayer matches. Deliberately separate from
    grant_game_reward(): single-player games have no server-side proof
    a win is legitimate (the client just reports a score), so that path
    needs the session-token + minimum-time anti-cheat. Multiplayer
    matches are different -- every move was already validated turn by
    turn by services/multiplayer_service.py's apply_move(), so the game
    ending IS the proof. This still requires a unique result_token
    (one per room+player) so the same match can't be paid out twice.
    """
    ensure_db()
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT 1 FROM game_results WHERE result_token = ?", (result_token,)
        ).fetchone()
        if existing is not None:
            raise DuplicateResultError(f"result_token {result_token!r} was already rewarded")

        if game_id not in REWARD_CURVES or tier not in REWARD_CURVES[game_id]:
            raise UnknownGameError(f"{game_id}:{tier}")
        c_lo, c_hi, x_lo, x_hi = REWARD_CURVES[game_id][tier]
        coins, xp = random.randint(c_lo, c_hi), random.randint(x_lo, x_hi)

        profile = get_profile(username)
        if profile is None:
            raise UnknownGameError(f"no such user: {username}")

        balance_before = profile["coins"]
        profile["coins"] = balance_before + coins
        profile["games_played"] = profile.get("games_played", 0) + 1
        if tier in _NON_WIN_TIERS:
            profile["current_streak"] = 0
        else:
            profile["games_won"] = profile.get("games_won", 0) + 1
            profile["current_streak"] = profile.get("current_streak", 0) + 1
            profile["best_streak"] = max(profile.get("best_streak", 0), profile["current_streak"])
        profile["favorite_game"] = profile.get("favorite_game") or game_id
        save_profile(username, profile)
        if xp:
            add_xp(username, xp)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            """INSERT INTO coin_transactions
               (username, type, amount, balance_before, balance_after, source, related_item, created_at)
               VALUES (?, 'GAME_REWARD', ?, ?, ?, ?, ?, ?)""",
            (username, coins, balance_before, balance_before + coins, game_id, tier, now),
        )
        conn.execute(
            """INSERT INTO game_results
               (username, game_id, result_token, outcome, coins_awarded, xp_awarded, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (username, game_id, result_token, tier, coins, xp, now),
        )
        conn.commit()
        return {"coins_awarded": coins, "xp_awarded": xp, "new_balance": balance_before + coins}
    finally:
        conn.close()


def grant_game_reward(username, game_id, tier, session_token):
    """
    The single entry point for awarding coins/XP for a completed
    single-player game. Requires a session_token from
    start_game_session() for THIS user and THIS game_id, not already
    redeemed, open at least as long as the claimed tier's minimum time.
    """
    ensure_db()
    conn = get_connection()
    try:
        session = conn.execute(
            "SELECT * FROM game_sessions WHERE session_token = ?", (session_token,)
        ).fetchone()
        if session is None:
            raise InvalidSessionError("no such session")
        if session["username"] != username:
            raise InvalidSessionError("session belongs to a different user")
        if session["game_id"] != game_id:
            raise InvalidSessionError("session was started for a different game")
        if session["used"]:
            raise DuplicateResultError("this session's result was already rewarded")

        if game_id == "omnivera":
            coins, xp = OMNIVERA_COINS, OMNIVERA_XP
        else:
            if game_id not in REWARD_CURVES or tier not in REWARD_CURVES[game_id]:
                raise UnknownGameError(f"{game_id}:{tier}")
            c_lo, c_hi, x_lo, x_hi = REWARD_CURVES[game_id][tier]
            coins, xp = random.randint(c_lo, c_hi), random.randint(x_lo, x_hi)

        started_at = datetime.strptime(session["started_at"], "%Y-%m-%d %H:%M:%S")
        elapsed = (datetime.now() - started_at).total_seconds()
        needed = _min_seconds_for(game_id, tier)
        if elapsed < needed:
            raise InvalidSessionError(
                f"claimed tier {tier!r} needs the session open >= {needed}s, only {elapsed:.1f}s elapsed"
            )

        profile = get_profile(username)
        if profile is None:
            raise UnknownGameError(f"no such user: {username}")

        balance_before = profile["coins"]
        profile["coins"] = balance_before + coins
        profile["games_played"] = profile.get("games_played", 0) + 1

        if tier in _NON_WIN_TIERS:
            profile["current_streak"] = 0
        else:
            profile["games_won"] = profile.get("games_won", 0) + 1
            profile["current_streak"] = profile.get("current_streak", 0) + 1
            profile["best_streak"] = max(profile.get("best_streak", 0), profile["current_streak"])

        profile["favorite_game"] = profile.get("favorite_game") or game_id
        save_profile(username, profile)

        if xp:
            add_xp(username, xp)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("UPDATE game_sessions SET used = 1 WHERE session_token = ?", (session_token,))
        conn.execute(
            """INSERT INTO coin_transactions
               (username, type, amount, balance_before, balance_after, source, related_item, created_at)
               VALUES (?, 'GAME_REWARD', ?, ?, ?, ?, ?, ?)""",
            (username, coins, balance_before, balance_before + coins, game_id, tier, now),
        )
        conn.execute(
            """INSERT INTO game_results
               (username, game_id, result_token, outcome, coins_awarded, xp_awarded, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (username, game_id, session_token, tier, coins, xp, now),
        )
        conn.commit()

        return {"coins_awarded": coins, "xp_awarded": xp, "new_balance": balance_before + coins}
    finally:
        conn.close()
