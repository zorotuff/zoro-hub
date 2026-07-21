import os
import json
import random
from datetime import datetime, timedelta

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
)

from profiles import (
    DATA_DIR,
    ensure_dirs,
    ensure_builtin_avatars,

    get_profile,
    create_profile,
    save_profile,
    update_profile,

    get_profile_path,
    username_exists,
    is_valid_username,

    avatar_url,
    banner_url,

    save_custom_avatar,
    save_custom_banner,
    set_builtin_avatar,

    win_rate,
)

app = Flask(__name__)

app.secret_key = "zoro_hub_secret"

app.permanent_session_lifetime = timedelta(days=30)

ensure_dirs()
ensure_builtin_avatars()

# ==========================================
# GAME CONSTANTS
# ==========================================

MIN_NUMBER = 1
MAX_NUMBER = 200

DEFAULT_DIFFICULTY = "medium"

DIFFICULTY_SETTINGS = {

    "easy": {
        "attempts": 15,
        "xp_reward": 25,
        "coin_reward": 10,
    },

    "medium": {
        "attempts": 10,
        "xp_reward": 50,
        "coin_reward": 20,
    },

    "hard": {
        "attempts": 7,
        "xp_reward": 100,
        "coin_reward": 40,
    },

}

# ==========================================
# HUB THEMES
# ==========================================

THEMES = {

    "obsidian": {
        "name": "Obsidian",
        "rarity": "Uncommon",
        "unlock_level": 1,
    },

    "aurora": {
        "name": "Aurora",
        "rarity": "Rare",
        "unlock_level": 5,
    },

    "nova": {
        "name": "Nova",
        "rarity": "Legendary",
        "unlock_level": 10,
    },

    "eclipse": {
        "name": "Eclipse",
        "rarity": "Mythic",
        "unlock_level": 20,
    },

}

# ==========================================
# LEVEL SYSTEM
# ==========================================

LEVEL_XP = [

    0,
    100,
    250,
    450,
    700,
    1000,
    1400,
    1900,
    2500,
    3200,
    4000,

]

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def current_config():

    difficulty = session.get(
        "difficulty",
        DEFAULT_DIFFICULTY
    )

    if difficulty not in DIFFICULTY_SETTINGS:

        difficulty = DEFAULT_DIFFICULTY

    return DIFFICULTY_SETTINGS[difficulty]


def get_user_profile():

    username = session.get("username")

    if not username:

        return None

    profile = get_profile(username)

    if profile is None:

        profile = create_profile(username)

    return profile


def save_user_profile(profile):

    username = session.get("username")

    if username:

        save_profile(username, profile)


def calculate_level(xp):

    level = 1

    for requirement in LEVEL_XP:

        if xp >= requirement:

            level += 1

    return max(1, level - 1)


def next_level_xp(level):

    if level >= len(LEVEL_XP):

        return LEVEL_XP[-1]

    return LEVEL_XP[level]


def xp_percent(profile):

    level = profile.get("level", 1)

    xp = profile.get("xp", 0)

    current = LEVEL_XP[level - 1]

    target = next_level_xp(level)

    if target == current:

        return 100

    return int(
        ((xp - current) / (target - current)) * 100
    )


def add_xp(profile, amount):

    old_level = profile.get("level", 1)

    profile["xp"] = profile.get("xp", 0) + amount

    profile["level"] = calculate_level(profile["xp"])

    # ==========================================
    # MYTHIC UNLOCK - GALAXY BORDER
    # ==========================================

    profile.setdefault("profile_unlocks", [])

    if (
        old_level < 25
        and profile["level"] >= 25
        and "galaxy_border" not in profile["profile_unlocks"]
    ):

        profile["profile_unlocks"].append("galaxy_border")

        session["new_unlock"] = {
            "type": "border",
            "name": "Galaxy Border",
            "rarity": "mythic"
        }

    return profile


def has_theme(profile, theme):

    level = profile.get("level", 1)

    required = THEMES[theme]["unlock_level"]

    return level >= required


def equipped_theme(profile):

    theme = profile.get(
        "profile_theme",
        "obsidian"
    )

    if theme not in THEMES:

        theme = "obsidian"

    return theme


def update_last_online(profile):

    profile["last_online"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    return profile

# ==========================================
# LOGIN / REGISTER
# ==========================================

@app.route("/", methods=["GET", "POST"])
def index():

    if "username" in session:
        return redirect(url_for("hub"))

    if request.method == "POST":

        action = request.form.get("action")

        username = request.form.get(
            "username",
            ""
        ).strip()

        if not is_valid_username(username):

            return render_template(
                "login.html",
                error="Invalid username."
            )

        # ------------------------
        # REGISTER
        # ------------------------

        if action == "register":

            if username_exists(username):

                return render_template(
                    "login.html",
                    error="Username already exists."
                )

            profile = create_profile(username)

            session["username"] = username
            session.permanent = True

            return redirect(url_for("hub"))

        # ------------------------
        # LOGIN
        # ------------------------

        if action == "login":

            if not username_exists(username):

                return render_template(
                    "login.html",
                    error="Account not found."
                )

            session["username"] = username
            session.permanent = True

            return redirect(url_for("hub"))

    return render_template(
        "login.html",
        error=None
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("index"))

# ==========================================
# HUB ROUTES
# ==========================================

@app.route("/hub")
def hub():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_user_profile()

    if profile is None:
        return redirect(url_for("logout"))

    profile = update_last_online(profile)

    save_user_profile(profile)

    profile["xp_percent"] = xp_percent(profile)

    profile["next_level_xp"] = next_level_xp(
        profile.get("level", 1)
    )

    system = {
        "cpu": "Intel Core i5-4310M",
        "gpu": "Intel HD Graphics 4600",
        "ram": "16 GB",
        "storage": "100 GB Free"
    }

    unlock_popup = session.pop("new_unlock", None)

    return render_template(

    "hub_v6.html",

    profile=profile,

    themes=THEMES,

    avatar_src=avatar_url(profile),

    banner_src=banner_url(profile),

    system=system,

    unlock_popup=unlock_popup,

)


@app.route("/hubv4")
def hub_v4():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_user_profile()

    if profile is None:
        return redirect(url_for("logout"))

    return render_template(

        "hub_v4.html",

        profile=profile,

        avatar_src=avatar_url(profile),

        banner_src=banner_url(profile),

    )


@app.route("/hubv6")
def hub_v6():

    return redirect(url_for("hub"))

# ==========================================
# GUESS THE NUMBER
# ==========================================

@app.route("/play")
def play():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_user_profile()

    config = current_config()

    session["secret_number"] = random.randint(
        MIN_NUMBER,
        MAX_NUMBER
    )

    session["attempts_left"] = config["attempts"]

    session["guess_history"] = []

    session["game_over"] = False

    session["won"] = False

    return redirect(url_for("game"))


@app.route("/game")
def game():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_user_profile()

    config = current_config()

    return render_template(

        "game.html",

        profile=profile,

        attempts=session.get(
            "attempts_left",
            config["attempts"]
        ),

        history=session.get(
            "guess_history",
            []
        ),

        game_over=session.get(
            "game_over",
            False
        ),

        won=session.get(
            "won",
            False
        ),

        difficulty=session.get(
            "difficulty",
            DEFAULT_DIFFICULTY
        ),

    )

# ==========================================
# TIC TAC TOE
# ==========================================

@app.route("/tic_tac_toe")
def tic_tac_toe():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_user_profile()

    if profile is None:
        return redirect(url_for("logout"))

    return render_template(

        "tictactoe.html",

        profile=profile,

        avatar_src=avatar_url(profile),

        banner_src=banner_url(profile)

    )

# =========================================
#kitty game
#==========================================

@app.route("/kitty_dash")
def kitty_dash():

    if "username" not in session:
        return redirect(url_for("index"))

    return render_template("kitty_dash.html")

# ==========================================
# PROCESS GUESS
# ==========================================

@app.route("/guess", methods=["POST"])
def guess():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_user_profile()

    if session.get("game_over"):
        return redirect(url_for("game"))

    config = current_config()

    try:

        guess = int(request.form.get("guess"))

    except:

        return redirect(url_for("game"))

    secret = session["secret_number"]

    attempts = session["attempts_left"]

    history = session.get("guess_history", [])

    result = ""

    if guess == secret:

        result = "correct"

        session["won"] = True

        session["game_over"] = True

        profile["games_played"] += 1

        profile["games_won"] += 1

        profile["current_streak"] += 1

        if profile["current_streak"] > profile["best_streak"]:

            profile["best_streak"] = profile["current_streak"]

        add_xp(
            profile,
            config["xp_reward"]
        )

    else:

        attempts -= 1

        session["attempts_left"] = attempts

        if guess < secret:

            result = "low"

        else:

            result = "high"

        if attempts <= 0:

            session["game_over"] = True

            session["won"] = False

            profile["games_played"] += 1

            profile["games_lost"] += 1

            profile["current_streak"] = 0

    distance = abs(secret - guess)

    hint = ""

    if result != "correct":

        if distance <= 3:

            hint = "🔥 Extremely Close"

        elif distance <= 10:

            hint = "🟢 Very Close"

        elif distance <= 20:

            hint = "🟡 Close"

        elif distance <= 40:

            hint = "🟠 Far"

        else:

            hint = "🔴 Very Far"

    history.append({

        "guess": guess,

        "result": result,

        "hint": hint

    })

    session["guess_history"] = history

    save_user_profile(profile)

    return redirect(url_for("game"))

# ==========================================
# PROFILE / THEME API
# ==========================================

@app.route("/api/equip_theme", methods=["POST"])
def equip_theme():

    if "username" not in session:
        return jsonify(success=False)

    profile = get_user_profile()

    data = request.get_json()

    theme = data.get("theme", "obsidian")

    if theme not in THEMES:

        return jsonify(
            success=False,
            message="Invalid theme."
        )

    if not has_theme(profile, theme):

        return jsonify(
            success=False,
            message="Theme locked."
        )

    profile["profile_theme"] = theme

    save_user_profile(profile)

    return jsonify(

        success=True,

        theme=theme

    )


@app.route("/profile")
def profile():

    if "username" not in session:
        return jsonify(success=False)

    profile = get_user_profile()

    profile["xp_percent"] = xp_percent(profile)

    profile["next_level_xp"] = next_level_xp(
        profile["level"]
    )

    return jsonify(

        success=True,

        profile=profile

    )


@app.route("/api/update_bio", methods=["POST"])
def update_bio():

    if "username" not in session:

        return jsonify(success=False)

    profile = get_user_profile()

    data = request.get_json()

    profile["biography"] = data.get(
        "bio",
        ""
    )[:200]

    save_user_profile(profile)

    return jsonify(success=True)


@app.route("/api/update_country", methods=["POST"])
def update_country():

    if "username" not in session:

        return jsonify(success=False)

    profile = get_user_profile()

    data = request.get_json()

    profile["country"] = data.get(
        "country",
        "Global Space"
    )[:40]

    save_user_profile(profile)

    return jsonify(success=True)

# ==========================================
# AVATAR / BANNER
# ==========================================

@app.route("/api/set_builtin_avatar", methods=["POST"])
def api_set_builtin_avatar():

    if "username" not in session:
        return jsonify(success=False)

    avatar = request.form.get("avatar")

    set_builtin_avatar(
        session["username"],
        avatar
    )

    return jsonify(success=True)


@app.route("/api/upload_avatar", methods=["POST"])
def api_upload_avatar():

    if "username" not in session:
        return jsonify(success=False)

    if "avatar" not in request.files:
        return jsonify(success=False)

    file = request.files["avatar"]

    save_custom_avatar(
        session["username"],
        file
    )

    return jsonify(success=True)


@app.route("/api/upload_banner", methods=["POST"])
def api_upload_banner():

    if "username" not in session:
        return jsonify(success=False)

    if "banner" not in request.files:
        return jsonify(success=False)

    file = request.files["banner"]

    save_custom_banner(
        session["username"],
        file
    )

    return jsonify(success=True)


# ==========================================
# LEADERBOARD
# ==========================================

@app.route("/leaderboard")
def leaderboard():

    ensure_dirs()

    players = []

    for file in os.listdir(DATA_DIR):

        if not file.endswith(".json"):
            continue

        path = os.path.join(
            DATA_DIR,
            file
        )

        with open(path, "r", encoding="utf-8") as f:

            profile = json.load(f)

        players.append(profile)

    players.sort(

        key=lambda x: (
            x.get("level", 1),
            x.get("xp", 0)
        ),

        reverse=True

    )

    return render_template(

        "leaderboard.html",

        players=players

    )

# ==========================================
# GAMES
# ==========================================

@app.route("/games")
def games():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_user_profile()

    if profile is None:
        return redirect(url_for("logout"))

    return render_template(
        "games.html",
        profile=profile,
        avatar_src=avatar_url(profile),
        banner_src=banner_url(profile),
    )


# ==========================================
# ACHIEVEMENTS
# ==========================================

@app.route("/achievements")
def achievements():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_user_profile()

    if profile is None:
        return redirect(url_for("logout"))

    return render_template(
        "achievements.html",
        profile=profile,
        avatar_src=avatar_url(profile),
        banner_src=banner_url(profile),
    )


# ==========================================
# SETTINGS
# ==========================================

@app.route("/settings")
def settings():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_user_profile()

    if profile is None:
        return redirect(url_for("logout"))

    return render_template(
        "settings.html",
        profile=profile,
        avatar_src=avatar_url(profile),
        banner_src=banner_url(profile),
    )

@app.route("/api/save_personalize", methods=["POST"])
def save_personalize():

    if "username" not in session:
        return jsonify(success=False)

    profile = get_user_profile()

    data = request.get_json()

    profile["avatar"] = data.get("avatar", profile.get("avatar", "😀"))
    profile["banner"] = data.get("banner", profile.get("banner", "Midnight"))
    profile["border"] = data.get("border", profile.get("border", "Default"))
    profile["theme"] = data.get("theme", profile.get("theme", "Dark"))
    profile["name_color"] = data.get("color", profile.get("name_color", "White"))
    profile["badge"] = data.get("badge", profile.get("badge", "🏆 Mythic"))

    save_user_profile(profile)

    return jsonify(success=True)

@app.route("/api/save_avatar", methods=["POST"])
def save_avatar():

    if "username" not in session:
        return jsonify(success=False)

    profile = get_user_profile()

    data = request.get_json()

    avatar = data.get("avatar")

    if avatar:
        profile["avatar"] = avatar
        print("Saving avatar:", avatar)
        print(profile)
    

    save_user_profile(profile)

    return jsonify(success=True)

@app.route("/equip_border", methods=["POST"])
def equip_border():

    if "username" not in session:
        return jsonify(success=False)

    profile = get_user_profile()

    if profile is None:
        return jsonify(success=False)

    data = request.get_json()

    border = data.get("border")

    if border == "galaxy":

        profile.setdefault("profile_unlocks", [])

        if "galaxy_border" not in profile["profile_unlocks"]:

            return jsonify(success=False)

    profile["avatar_border"] = border

    save_user_profile(profile)

    return jsonify(success=True)

# ==========================================
# SYSTEM INFO
# ==========================================

@app.route("/api/system")
def api_system():

    return jsonify({

        "cpu": "Intel Core i2-4310M",

        "gpu": "Intel 144p potato Graphics 460",

        "ram": "-12 GB",

        "storage": "10 GB Free"

    })


# ==========================================
# ERROR PAGES
# ==========================================

@app.errorhandler(404)
def page_not_found(e):

    return render_template(
        "404.html"
    ), 404


@app.errorhandler(500)
def server_error(e):

    return render_template(
        "500.html"
    ), 500

@app.route("/personalize")
def personalize():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_user_profile()

    if profile is None:
        return redirect(url_for("logout"))

    return render_template(

        "personalize.html",

        profile=profile,

        avatar_src=avatar_url(profile),

        banner_src=banner_url(profile),

    )

def avatar_url(profile):

    avatar = profile.get("avatar", "avatar1.png")

    if avatar.endswith(".png") or avatar.endswith(".jpg") or avatar.endswith(".jpeg"):

        return f"/static/img/avatars/{avatar}"

    return f"/static/img/avatars/{avatar}.png"

    


def banner_url(profile):

    banner = profile.get("profile_banner", "default")

    return f"/static/img/banners/{banner}.png"

# ==========================================
# RUN APP
# ==========================================

if __name__ == "__main__":

    app.run(

        debug=True

    )