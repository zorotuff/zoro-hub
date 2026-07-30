import random

MIN_NUMBER = 1
MAX_NUMBER = 200

DEFAULT_DIFFICULTY = "medium"

DIFFICULTY_SETTINGS = {

    "easy": {
        "attempts": 15,
        "label": "Easy",
        "min": 1,
        "max": 200,
        "xp_reward": 25,
    },

    "medium": {
        "attempts": 10,
        "label": "Medium",
        "min": 1,
        "max": 200,
        "xp_reward": 50,
    },

    "hard": {
        "attempts": 7,
        "label": "Hard",
        "min": 1,
        "max": 200,
        "xp_reward": 100,
    },

}


def current_config(session):

    difficulty = session.get(
        "difficulty",
        DEFAULT_DIFFICULTY
    )

    return DIFFICULTY_SETTINGS.get(
        difficulty,
        DIFFICULTY_SETTINGS[DEFAULT_DIFFICULTY]
    )


def start_game(session):

    config = current_config(session)

    session["secret_number"] = random.randint(
        MIN_NUMBER,
        MAX_NUMBER
    )

    session["attempts_left"] = config["attempts"]

    session["guess_history"] = []

    session["game_over"] = False

    session["won"] = False

    session["hints_remaining"] = 3

    session["last_hint"] = ""

    return config