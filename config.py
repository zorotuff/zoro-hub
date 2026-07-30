# ==========================================
# ZORO HUB CONFIG
# ==========================================

SECRET_KEY = "zoro_hub_secret"

DEFAULT_DIFFICULTY = "medium"

MIN_NUMBER = 1
MAX_NUMBER = 200

# ==========================================
# GUESS THE NUMBER
# ==========================================

GTN_CONFIG = {

    "easy": {

        "attempts": 15,
        "xp": 25,
        "coins": 10,

    },

    "medium": {

        "attempts": 10,
        "xp": 50,
        "coins": 20,

    },

    "hard": {

        "attempts": 7,
        "xp": 100,
        "coins": 40,

    },

    "asian": {

        "attempts": 5,
        "xp": 150,
        "coins": 60,

    }

}

# ==========================================
# TIC TAC TOE
# ==========================================

TTT_REWARDS = {

    "easy": {

        "win": 20,
        "draw": 10,
        "lose": 5

    },

    "medium": {

        "win": 45,
        "draw": 15,
        "lose": 5

    },

    "hard": {

        "win": 80,
        "draw": 20,
        "lose": 5

    }

}

# ==========================================
# THEMES
# ==========================================

THEMES = {

    "obsidian": 1,
    "aurora": 5,
    "nova": 10,
    "eclipse": 20

}