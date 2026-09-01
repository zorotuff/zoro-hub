# ==========================================
# ZORO HUB CONFIG
# ==========================================

import os
import secrets

# In production, set ZORO_SECRET_KEY yourself (e.g. `export ZORO_SECRET_KEY=...`)
# so sessions survive restarts and aren't signed with a key anyone can read
# in this file. Falling back to a random key locally is safer than a
# hardcoded one, but it does mean local sessions reset each time the app
# starts without the env var set.
SECRET_KEY = os.environ.get("ZORO_SECRET_KEY") or secrets.token_hex(32)

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