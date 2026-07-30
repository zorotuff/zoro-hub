from security.database import load_accounts, save_accounts
from security.auth import hash_password, verify_password


def account_exists(username):
    accounts = load_accounts()
    return username.lower() in accounts


def create_account(username, password):

    accounts = load_accounts()

    username = username.lower()

    if username in accounts:
        return False

    accounts[username] = {

        "password": hash_password(password),

        "admin": False

    }

    save_accounts(accounts)

    return True


def login_account(username, password):

    accounts = load_accounts()

    username = username.lower()

    if username not in accounts:
        return False

    return verify_password(
        password,
        accounts[username]["password"]
    )


def is_admin(username):

    accounts = load_accounts()

    username = username.lower()

    if username not in accounts:
        return False

    return accounts[username].get("admin", False)