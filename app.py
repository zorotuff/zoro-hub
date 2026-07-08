"""
Guess The Number - Flask Web Game
-----------------------------------
A clean, single-file Flask application implementing:
  - Difficulty levels (Easy / Medium / Hard)
  - Hearts / limited attempts
  - Hint system
  - Previous guess history
  - Scoring + win streak tracking
  - Persistent High Score (highscore.txt)
  - Persistent Statistics (stats.json)
  - Win / Lose pages

The module is organized as:
  1. Configuration & constants
  2. Persistence helpers (highscore + stats files)
  3. Game-state helpers (session management)
  4. Scoring helpers
  5. Routes
"""

import json
import os
import random
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret-in-production"  # required for sessions

# ---------------------------------------------------------------------------
# 1. Configuration & constants
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscore.txt")
STATS_FILE = os.path.join(BASE_DIR, "stats.json")

DIFFICULTY_SETTINGS = {
    "easy": {
        "label": "Easy",
        "min_number": 1,
        "max_number": 50,
        "max_attempts": 10,
        "max_hints": 3,
        "score_multiplier": 1,
    },
    "medium": {
        "label": "Medium",
        "min_number": 1,
        "max_number": 100,
        "max_attempts": 7,
        "max_hints": 2,
        "score_multiplier": 2,
    },
    "hard": {
        "label": "Hard",
        "min_number": 1,
        "max_number": 200,
        "max_attempts": 5,
        "max_hints": 1,
        "score_multiplier": 3,
    },
}

DEFAULT_DIFFICULTY = "medium"


# ---------------------------------------------------------------------------
# 2. Persistence helpers
# ---------------------------------------------------------------------------

def load_highscore():
    """Read the all-time high score from highscore.txt. Returns 0 if missing/invalid."""
    if not os.path.exists(HIGHSCORE_FILE):
        return 0
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            content = f.read().strip()
            return int(content) if content else 0
    except (ValueError, IOError):
        return 0


def save_highscore(score):
    """Persist a new high score to highscore.txt."""
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))


def update_highscore_if_needed(score):
    """Compare score against stored high score; save + return True if it's a new record."""
    current_high = load_highscore()
    if score > current_high:
        save_highscore(score)
        return True, score
    return False, current_high


def load_stats():
    """Load cumulative game statistics from stats.json (auto-created on first write)."""
    default_stats = {
        "games_played": 0,
        "games_won": 0,
        "games_lost": 0,
        "total_score": 0,
        "best_streak": 0,
        "hints_used_total": 0,
    }
    if not os.path.exists(STATS_FILE):
        return default_stats
    try:
        with open(STATS_FILE, "r") as f:
            data = json.load(f)
            default_stats.update(data)
            return default_stats
    except (json.JSONDecodeError, IOError):
        return default_stats


def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)


def update_stats(won, score, streak, hints_used):
    """Update and persist cumulative statistics after a game ends."""
    stats = load_stats()
    stats["games_played"] += 1
    stats["games_won"] += 1 if won else 0
    stats["games_lost"] += 0 if won else 1
    stats["total_score"] += score
    stats["best_streak"] = max(stats["best_streak"], streak)
    stats["hints_used_total"] += hints_used
    save_stats(stats)
    return stats


# ---------------------------------------------------------------------------
# 3. Game-state helpers (Flask session)
# ---------------------------------------------------------------------------

def start_new_game(difficulty):
    """Initialize a fresh game in the session for the given difficulty."""
    config = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS[DEFAULT_DIFFICULTY])
    secret_number = random.randint(config["min_number"], config["max_number"])

    # Preserve win streak across games; reset everything else.
    streak = session.get("streak", 0)

    session["difficulty"] = difficulty
    session["secret_number"] = secret_number
    session["min_number"] = config["min_number"]
    session["max_number"] = config["max_number"]
    session["max_attempts"] = config["max_attempts"]
    session["attempts_left"] = config["max_attempts"]
    session["max_hints"] = config["max_hints"]
    session["hints_used"] = 0
    session["guesses"] = []
    session["streak"] = streak
    session["game_over"] = False


def has_active_game():
    """Check whether a game is currently in progress in the session."""
    return "secret_number" in session and not session.get("game_over", True)


def get_game_state():
    """Return a dict of the current game state, safe to pass into templates."""
    return {
        "difficulty": session.get("difficulty"),
        "difficulty_label": DIFFICULTY_SETTINGS.get(
            session.get("difficulty", DEFAULT_DIFFICULTY), {}
        ).get("label"),
        "min_number": session.get("min_number"),
        "max_number": session.get("max_number"),
        "max_attempts": session.get("max_attempts"),
        "attempts_left": session.get("attempts_left"),
        "max_hints": session.get("max_hints"),
        "hints_used": session.get("hints_used"),
        "hints_remaining": session.get("max_hints", 0) - session.get("hints_used", 0),
        "guesses": session.get("guesses", []),
        "streak": session.get("streak", 0),
    }


def record_guess(guess, result):
    """Append a guess + its result ('higher' / 'lower' / 'correct') to the session history."""
    guesses = session.get("guesses", [])
    guesses.append({"value": guess, "result": result})
    session["guesses"] = guesses


# ---------------------------------------------------------------------------
# 4. Scoring helpers
# ---------------------------------------------------------------------------

def calculate_score(difficulty, max_attempts, attempts_left, hints_used):
    """
    Score formula:
      - Reward remaining attempts (fewer guesses used = higher score)
      - Scale by difficulty multiplier
      - Penalize hint usage
    """
    config = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS[DEFAULT_DIFFICULTY])
    multiplier = config["score_multiplier"]

    base_score = attempts_left * 10 * multiplier
    hint_penalty = hints_used * 15
    score = max(0, base_score - hint_penalty)
    return score


def get_hint(secret_number, min_number, max_number, guesses):
    """
    Generate a simple hint based on how many hints have already been used:
      1st hint -> odd/even
      2nd hint -> which half of the range the number is in
      3rd+ hint -> distance band (how close recent guesses have been)
    """
    hints_used = session.get("hints_used", 0)

    if hints_used == 0:
        parity = "even" if secret_number % 2 == 0 else "odd"
        return f"The number is {parity}."
    elif hints_used == 1:
        midpoint = (min_number + max_number) // 2
        half = "lower half" if secret_number <= midpoint else "upper half"
        return f"The number is in the {half} of the range ({min_number}-{max_number})."
    else:
        digit_sum = sum(int(d) for d in str(secret_number))
        return f"The digits of the number add up to {digit_sum}."


# ---------------------------------------------------------------------------
# 5. Routes
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template("hub.html")


@app.route("/menu", methods=["GET", "POST"])
def menu():
    """Show difficulty selection; on POST, start a new game and go to /game."""
    if request.method == "POST":
        difficulty = request.form.get("difficulty", DEFAULT_DIFFICULTY)
        if difficulty not in DIFFICULTY_SETTINGS:
            difficulty = DEFAULT_DIFFICULTY
        start_new_game(difficulty)
        return redirect(url_for("game"))

    high_score = load_highscore()
    return render_template(
        "menu.html",
        difficulties=DIFFICULTY_SETTINGS,
        high_score=high_score,
        streak=session.get("streak", 0),
    )


@app.route("/game", methods=["GET", "POST"])
def game():
    """Main gameplay route: display the game, process guesses and hint requests."""
    if not has_active_game():
        return redirect(url_for("menu"))

    message = None

    if request.method == "POST":
        action = request.form.get("action", "guess")

        # --- Hint request -----------------------------------------------
        if action == "hint":
            if session["hints_used"] < session["max_hints"]:
                hint_text = get_hint(
                    session["secret_number"],
                    session["min_number"],
                    session["max_number"],
                    session.get("guesses", []),
                )
                session["hints_used"] += 1
                message = hint_text
            else:
                message = "No hints remaining!"

        # --- Guess submission ---------------------------------------------
        else:
            guess_raw = request.form.get("guess", "")
            try:
                guess = int(guess_raw)
            except ValueError:
                message = "Please enter a valid whole number."
                return render_template(
                    "game.html", **get_game_state(), message=message
                )

            if guess < session["min_number"] or guess > session["max_number"]:
                message = (
                    f"Guess must be between {session['min_number']} "
                    f"and {session['max_number']}."
                )
                return render_template(
                    "game.html", **get_game_state(), message=message
                )

            secret_number = session["secret_number"]

            if guess == secret_number:
                record_guess(guess, "correct")
                session["attempts_left"] -= 0  # correct guess doesn't cost an attempt penalty
                score = calculate_score(
                    session["difficulty"],
                    session["max_attempts"],
                    session["attempts_left"],
                    session["hints_used"],
                )
                session["streak"] = session.get("streak", 0) + 1
                session["game_over"] = True

                is_new_record, high_score = update_highscore_if_needed(score)
                update_stats(
                    won=True,
                    score=score,
                    streak=session["streak"],
                    hints_used=session["hints_used"],
                )

                session["last_score"] = score
                session["last_new_record"] = is_new_record
                return redirect(url_for("win"))

            # Wrong guess
            result = "lower" if guess > secret_number else "higher"
            record_guess(guess, result)
            session["attempts_left"] -= 1

            if session["attempts_left"] <= 0:
                session["streak"] = 0
                session["game_over"] = True
                update_stats(
                    won=False,
                    score=0,
                    streak=0,
                    hints_used=session["hints_used"],
                )
                return redirect(url_for("lose"))

            message = f"Try {result}!"

    return render_template("game.html", **get_game_state(), message=message)


@app.route("/win")
def win():
    """Show the win page for the most recently completed (won) game."""
    return render_template(
        "win.html",
        score=session.get("last_score", 0),
        new_record=session.get("last_new_record", False),
        high_score=load_highscore(),
        streak=session.get("streak", 0),
        difficulty_label=DIFFICULTY_SETTINGS.get(
            session.get("difficulty", DEFAULT_DIFFICULTY), {}
        ).get("label"),
        attempts_used=session.get("max_attempts", 0) - session.get("attempts_left", 0),
        guesses=session.get("guesses", []),
    )


@app.route("/lose")
def lose():
    """Show the lose page for the most recently completed (lost) game."""
    return render_template(
        "lose.html",
        secret_number=session.get("secret_number"),
        high_score=load_highscore(),
        difficulty_label=DIFFICULTY_SETTINGS.get(
            session.get("difficulty", DEFAULT_DIFFICULTY), {}
        ).get("label"),
        guesses=session.get("guesses", []),
    )


@app.route("/stats")
def stats():
    """Show cumulative statistics across all games."""
    data = load_stats()
    win_rate = (
        round((data["games_won"] / data["games_played"]) * 100, 1)
        if data["games_played"] > 0
        else 0
    )
    return render_template(
        "stats.html",
        stats=data,
        win_rate=win_rate,
        high_score=load_highscore(),
        current_streak=session.get("streak", 0),
    )


@app.route("/highscore")
def highscore():
    """Show the high score page."""
    return render_template("highscore.html", high_score=load_highscore())


@app.route("/reset", methods=["POST"])
def reset():
    """Abandon the current game and return to the menu (does not affect stats/high score)."""
    session.pop("secret_number", None)
    session["game_over"] = True
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)