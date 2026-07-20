import os
import json
import uuid
from datetime import date, datetime

# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "profiles")

AVATAR_DIR = os.path.join(BASE_DIR, "static", "avatars")

BANNER_DIR = os.path.join(BASE_DIR, "static", "banners")

BUILTIN_AVATAR_DIR = os.path.join(
    BASE_DIR,
    "static",
    "img",
    "avatars"
)

BUILTIN_BANNER_DIR = os.path.join(
    BASE_DIR,
    "static",
    "img",
    "banners"
)

# ==========================================
# DEFAULTS
# ==========================================

DEFAULT_THEME = "obsidian"

DEFAULT_AVATAR = "shadow-assassin"

DEFAULT_BANNER = "default"

DEFAULT_COUNTRY = "Global Space"

# ==========================================
# DIRECTORY HELPERS
# ==========================================

def ensure_dirs():

    os.makedirs(DATA_DIR, exist_ok=True)

    os.makedirs(AVATAR_DIR, exist_ok=True)

    os.makedirs(BANNER_DIR, exist_ok=True)


def ensure_builtin_avatars():

    os.makedirs(BUILTIN_AVATAR_DIR, exist_ok=True)

    os.makedirs(BUILTIN_BANNER_DIR, exist_ok=True)


# ==========================================
# PROFILE PATH
# ==========================================

def get_profile_path(username):

    username = username.lower()

    return os.path.join(
        DATA_DIR,
        f"{username}.json"
    )


# ==========================================
# USERNAME
# ==========================================

def is_valid_username(username):

    if not isinstance(username, str):
        return False

    username = username.strip()

    if len(username) < 3:
        return False

    if len(username) > 20:
        return False

    return username.isalnum()


def username_exists(username):

    return os.path.exists(
        get_profile_path(username)
    )

# ==========================================
# PROFILE CREATION
# ==========================================

def get_default_profile(username):

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

        "favorite_game": "Guess The Number",

        "biography": "Welcome to my profile.",

        "country": DEFAULT_COUNTRY,

        "joined_date": date.today().strftime("%B %Y"),

        "account_creation_date": datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        ),

        "last_online": "Just Now",

        "online_status": "offline",

        "avatar": DEFAULT_AVATAR,

        "avatar_type": "builtin",

        "avatar_border": "none",

        "profile_banner": DEFAULT_BANNER,

        "profile_theme": DEFAULT_THEME,

        "hub_version": "v6",

        "achievements": [],

        "badges": ["Member"]

    }


# ==========================================
# LOAD PROFILE
# ==========================================

def get_profile(username):

    path = get_profile_path(username)

    if not os.path.exists(path):

        return None

    with open(path, "r", encoding="utf-8") as f:

        profile = json.load(f)

    return profile


# ==========================================
# CREATE PROFILE
# ==========================================

def create_profile(username):

    ensure_dirs()

    profile = get_default_profile(username)

    save_profile(username, profile)

    return profile


# ==========================================
# SAVE PROFILE
# ==========================================

def save_profile(username, profile):

    ensure_dirs()

    path = get_profile_path(username)

    with open(path, "w", encoding="utf-8") as f:

        json.dump(
            profile,
            f,
            indent=4
        )

    return profile

# ==========================================
# PROFILE UPDATE
# ==========================================

def update_profile(username, **kwargs):

    profile = get_profile(username)

    if profile is None:

        profile = create_profile(username)

    for key, value in kwargs.items():

        profile[key] = value

    profile["last_online"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    save_profile(
        username,
        profile
    )

    return profile


# ==========================================
# PROFILE STATS
# ==========================================

def win_rate(profile):

    played = profile.get(
        "games_played",
        0
    )

    if played == 0:

        return 0.0

    return round(

        (profile.get("games_won", 0) / played) * 100,

        1

    )


# ==========================================
# LEVEL HELPERS
# ==========================================

def add_xp(profile, amount):

    profile["xp"] = profile.get("xp", 0) + amount

    while profile["xp"] >= profile["level"] * 100:

        profile["xp"] -= profile["level"] * 100

        profile["level"] += 1

    return profile


# ==========================================
# ACHIEVEMENTS
# ==========================================

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


# ==========================================
# BADGES
# ==========================================

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

    return "/static/img/avatars/" + profile.get(
        "avatar",
        DEFAULT_AVATAR
    ) + ".png"


def banner_url(profile):

    banner = profile.get(
        "profile_banner",
        DEFAULT_BANNER
    )

    if banner.startswith("custom_"):

        return "/static/banners/" + banner

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

    filename = f"{username}_avatar.png"

    filepath = os.path.join(
        AVATAR_DIR,
        filename
    )

    file.save(filepath)

    profile["avatar"] = filename

    profile["avatar_type"] = "custom"

    save_profile(username, profile)

    return profile


def save_custom_banner(username, file):

    profile = get_profile(username)

    if profile is None:

        return None

    filename = f"{username}_banner.png"

    filepath = os.path.join(
        BANNER_DIR,
        filename
    )

    file.save(filepath)

    profile["profile_banner"] = filename

    save_profile(username, profile)

    return profile


# ==========================================
# EXPORTS
# ==========================================

__all__ = [

    "DATA_DIR",

    "ensure_dirs",
    "ensure_builtin_avatars",

    "get_profile_path",

    "username_exists",
    "is_valid_username",

    "get_default_profile",

    "get_profile",
    "create_profile",
    "save_profile",
    "update_profile",

    "win_rate",
    "add_xp",

    "evaluate_achievements",
    "evaluate_badges",

    "avatar_url",
    "banner_url",

    "set_builtin_avatar",

    "save_custom_avatar",
    "save_custom_banner",

]