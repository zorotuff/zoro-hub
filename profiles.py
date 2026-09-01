import os
import json
import uuid
from datetime import date, datetime

from security.database import get_connection, ensure_db

# ==========================================
# DEFAULTS
# ==========================================

DEFAULT_THEME = ""  # empty = hub_v6.css's own built-in colors; "obsidian" matched no real class
DEFAULT_AVATAR = "shadow-assassin"
DEFAULT_BANNER = "default"
DEFAULT_COUNTRY = "Global Space"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AVATAR_DIR = os.path.join(BASE_DIR, "static", "avatars")
BANNER_DIR = os.path.join(BASE_DIR, "static", "banners")


def ensure_dirs():
    os.makedirs(AVATAR_DIR, exist_ok=True)
    os.makedirs(BANNER_DIR, exist_ok=True)


# ==========================================
# USERNAME
# ==========================================

def is_valid_username(username):
    if not isinstance(username, str):
        return False
    username = username.strip()
    if len(username) < 3 or len(username) > 20:
        return False
    return username.isalnum()


def username_exists(username):
    ensure_db()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT 1 FROM users WHERE username = ?", (username.lower(),)
        ).fetchone()
        return row is not None
    finally:
        conn.close()


# ==========================================
# ROW <-> PROFILE DICT
# ==========================================

def _row_to_profile(row):
    if row is None:
        return None
    profile = dict(row)
    profile.pop("password_hash", None)  # never leak the hash into a profile dict
    profile["achievements"] = json.loads(profile.get("achievements") or "[]")
    profile["badges"] = json.loads(profile.get("badges") or '["Member"]')
    profile["profile_unlocks"] = json.loads(profile.get("profile_unlocks") or "[]")
    profile["admin"] = bool(profile.pop("is_admin", 0))
    return profile


def get_default_profile(username):
    now = datetime.now()
    return {
        "username": username,
        "uid": f"NX-{uuid.uuid4().hex[:8].upper()}",
        "level": 1,
        "xp": 0,
        "coins": 0,
        "profile_unlocks": [],
        "games_played": 0,
        "games_won": 0,
        "games_lost": 0,
        "current_streak": 0,
        "best_streak": 0,
        "favorite_game": None,
        "biography": "Welcome to my profile.",
        "country": DEFAULT_COUNTRY,
        "joined_date": date.today().strftime("%B %Y"),
        "account_creation_date": now.strftime("%Y-%m-%d %H:%M"),
        "last_online": "Just Now",
        "online_status": "offline",
        "avatar": DEFAULT_AVATAR,
        "avatar_type": "builtin",
        "avatar_border": "none",
        "profile_banner": DEFAULT_BANNER,
        "profile_theme": DEFAULT_THEME,
        "hub_version": "v6",
        "achievements": [],
        "badges": ["Member"],
    }


# ==========================================
# LOAD / CREATE / SAVE
# ==========================================

def get_profile(username):
    ensure_db()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username.lower(),)
        ).fetchone()
        return _row_to_profile(row)
    finally:
        conn.close()


def create_profile(username):
    """
    Profile fields live on the same `users` row as the account, which
    create_account() normally creates first. This is a defensive
    fallback for the (unusual) case where a profile is requested before
    the account row exists -- if the row's already there, it's a no-op.
    """
    ensure_db()
    existing = get_profile(username)
    if existing is not None:
        return existing

    conn = get_connection()
    try:
        d = get_default_profile(username)
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn.execute(
            """
            INSERT INTO users (
                username, uid, password_hash, is_admin,
                level, xp, coins, favorite_game,
                biography, country, joined_date, account_creation_date,
                last_online, online_status
            ) VALUES (?,?,?,0,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                username.lower(), d["uid"], "",
                d["level"], d["xp"], d["coins"], d["favorite_game"],
                d["biography"], d["country"], d["joined_date"], d["account_creation_date"],
                now, d["online_status"],
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return get_profile(username)


def save_profile(username, profile):
    ensure_db()
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE users SET
                level = ?, xp = ?, coins = ?,
                games_played = ?, games_won = ?, games_lost = ?,
                current_streak = ?, best_streak = ?, favorite_game = ?,
                biography = ?, country = ?,
                avatar = ?, avatar_type = ?, avatar_border = ?,
                profile_banner = ?, profile_theme = ?, hub_version = ?,
                achievements = ?, badges = ?, profile_unlocks = ?,
                last_online = ?, online_status = ?
            WHERE username = ?
            """,
            (
                profile.get("level", 1), profile.get("xp", 0), profile.get("coins", 0),
                profile.get("games_played", 0), profile.get("games_won", 0), profile.get("games_lost", 0),
                profile.get("current_streak", 0), profile.get("best_streak", 0), profile.get("favorite_game"),
                profile.get("biography", ""), profile.get("country", DEFAULT_COUNTRY),
                profile.get("avatar", DEFAULT_AVATAR), profile.get("avatar_type", "builtin"),
                profile.get("avatar_border", "none"),
                profile.get("profile_banner", DEFAULT_BANNER), profile.get("profile_theme", DEFAULT_THEME),
                profile.get("hub_version", "v6"),
                json.dumps(profile.get("achievements", [])),
                json.dumps(profile.get("badges", ["Member"])),
                json.dumps(profile.get("profile_unlocks", [])),
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                profile.get("online_status", "offline"),
                username.lower(),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return profile


def update_profile(username, **kwargs):
    profile = get_profile(username)
    if profile is None:
        profile = create_profile(username)
    for key, value in kwargs.items():
        profile[key] = value
    save_profile(username, profile)
    return profile


# ==========================================
# STATS / LEVEL / ACHIEVEMENTS (pure logic, unchanged from before)
# ==========================================

def win_rate(profile):
    played = profile.get("games_played", 0)
    if played == 0:
        return 0.0
    return round((profile.get("games_won", 0) / played) * 100, 1)


def add_xp(username, amount):
    profile = get_profile(username)
    if profile is None:
        return None

    profile["xp"] += amount
    while profile["xp"] >= profile["level"] * 100:
        profile["xp"] -= profile["level"] * 100
        profile["level"] += 1

    evaluate_achievements(profile)
    evaluate_badges(profile)
    save_profile(username, profile)
    return profile


def evaluate_achievements(profile):
    achievements = []
    wins = profile.get("games_won", 0)
    level = profile.get("level", 1)
    if wins >= 1:
        achievements.append("First Victory")
    if wins >= 10:
        achievements.append("Experienced")
    if wins >= 50:
        achievements.append("Champion")
    if level >= 5:
        achievements.append("Level 5")
    if level >= 10:
        achievements.append("Level 10")
    if level >= 20:
        achievements.append("Level 20")
    profile["achievements"] = achievements
    return profile


def evaluate_badges(profile):
    badges = ["Member"]
    if profile.get("games_won", 0) >= 25:
        badges.append("Champion")
    if profile.get("level", 1) >= 10:
        badges.append("Elite")
    if profile.get("best_streak", 0) >= 10:
        badges.append("Hot Streak")
    profile["badges"] = badges
    return profile


# ==========================================
# AVATAR / BANNER HELPERS
# ==========================================

def avatar_url(profile):
    if profile.get("avatar_type") == "custom":
        return "/static/avatars/" + profile["avatar"]
    if profile.get("avatar_type") == "shop":
        # Real, purpose-made art for shop-exclusive avatars -- not the
        # builtin picker's /static/img/avatars/ path, which doesn't
        # have these files and would 404.
        return "/static/avatars/" + profile.get("avatar", DEFAULT_AVATAR) + ".svg"
    return "/static/img/avatars/" + profile.get("avatar", DEFAULT_AVATAR) + ".png"


def banner_url(profile):
    banner = profile.get("profile_banner", DEFAULT_BANNER)
    if banner.startswith("custom_"):
        return "/static/banners/" + banner
    if banner.startswith("banner_"):
        return "/static/banners/" + banner + ".svg"
    return "/static/img/banners/" + banner + ".png"


def set_builtin_avatar(username, avatar):
    profile = get_profile(username)
    if profile is None:
        return None
    profile["avatar"] = avatar
    profile["avatar_type"] = "builtin"
    save_profile(username, profile)
    return profile


def save_custom_avatar(username, file):
    profile = get_profile(username)
    if profile is None:
        return None
    ensure_dirs()
    filename = f"{username}_avatar.png"
    file.save(os.path.join(AVATAR_DIR, filename))
    profile["avatar"] = filename
    profile["avatar_type"] = "custom"
    save_profile(username, profile)
    return profile


def save_custom_banner(username, file):
    profile = get_profile(username)
    if profile is None:
        return None
    ensure_dirs()
    filename = f"{username}_banner.png"
    file.save(os.path.join(BANNER_DIR, filename))
    profile["profile_banner"] = filename
    save_profile(username, profile)
    return profile


__all__ = [
    "ensure_dirs",
    "username_exists", "is_valid_username",
    "get_default_profile",
    "get_profile", "create_profile", "save_profile", "update_profile",
    "win_rate", "add_xp",
    "evaluate_achievements", "evaluate_badges",
    "avatar_url", "banner_url",
    "set_builtin_avatar", "save_custom_avatar", "save_custom_banner",
]
