import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASE_DIR = os.path.join(BASE_DIR, "database")

ACCOUNTS_FILE = os.path.join(DATABASE_DIR, "accounts.json")


def ensure_database():

    os.makedirs(DATABASE_DIR, exist_ok=True)

    if not os.path.exists(ACCOUNTS_FILE):

        with open(ACCOUNTS_FILE, "w") as f:

            json.dump({}, f, indent=4)


def load_accounts():

    ensure_database()

    with open(ACCOUNTS_FILE, "r") as f:

        return json.load(f)


def save_accounts(accounts):

    with open(ACCOUNTS_FILE, "w") as f:

        json.dump(accounts, f, indent=4)