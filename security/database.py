import os
import json
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DATABASE_DIR, "zoro_hub.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    username        TEXT PRIMARY KEY,
    uid             TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    is_admin        INTEGER NOT NULL DEFAULT 0,
    role            TEXT NOT NULL DEFAULT 'user',
    suspended       INTEGER NOT NULL DEFAULT 0,
    suspend_reason  TEXT,
    leaderboard_visible INTEGER NOT NULL DEFAULT 1,

    level           INTEGER NOT NULL DEFAULT 1,
    xp              INTEGER NOT NULL DEFAULT 0,
    coins           INTEGER NOT NULL DEFAULT 0,

    games_played    INTEGER NOT NULL DEFAULT 0,
    games_won       INTEGER NOT NULL DEFAULT 0,
    games_lost      INTEGER NOT NULL DEFAULT 0,
    current_streak  INTEGER NOT NULL DEFAULT 0,
    best_streak     INTEGER NOT NULL DEFAULT 0,
    favorite_game   TEXT,

    biography       TEXT NOT NULL DEFAULT 'Welcome to my profile.',
    country         TEXT NOT NULL DEFAULT 'Global Space',

    avatar          TEXT NOT NULL DEFAULT 'shadow-assassin',
    avatar_type     TEXT NOT NULL DEFAULT 'builtin',
    avatar_border   TEXT NOT NULL DEFAULT 'none',
    profile_banner  TEXT NOT NULL DEFAULT 'default',
    profile_theme   TEXT NOT NULL DEFAULT '',
    hub_version     TEXT NOT NULL DEFAULT 'v6',

    achievements    TEXT NOT NULL DEFAULT '[]',
    badges          TEXT NOT NULL DEFAULT '["Member"]',
    profile_unlocks TEXT NOT NULL DEFAULT '[]',

    joined_date            TEXT NOT NULL,
    account_creation_date  TEXT NOT NULL,
    last_online             TEXT,
    online_status           TEXT NOT NULL DEFAULT 'offline'
);

CREATE TABLE IF NOT EXISTS coin_transactions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT NOT NULL REFERENCES users(username),
    type            TEXT NOT NULL,
    amount          INTEGER NOT NULL,
    balance_before  INTEGER NOT NULL,
    balance_after   INTEGER NOT NULL,
    source          TEXT,
    related_item    TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    session_token   TEXT PRIMARY KEY,
    username        TEXT NOT NULL REFERENCES users(username),
    game_id         TEXT NOT NULL,
    started_at      TEXT NOT NULL,
    used            INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_inventory (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT NOT NULL REFERENCES users(username),
    item_id         TEXT NOT NULL,
    acquired_at     TEXT NOT NULL,
    UNIQUE(username, item_id)
);

CREATE TABLE IF NOT EXISTS admin_audit_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_username  TEXT NOT NULL,
    admin_role      TEXT NOT NULL,
    action          TEXT NOT NULL,
    target_type     TEXT NOT NULL,
    target_id       TEXT,
    previous_state  TEXT,
    new_state       TEXT,
    reason          TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    reporter        TEXT NOT NULL,
    target_username TEXT NOT NULL,
    reason          TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'open',
    created_at      TEXT NOT NULL,
    resolved_by     TEXT,
    resolved_at     TEXT
);

CREATE TABLE IF NOT EXISTS game_results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT NOT NULL REFERENCES users(username),
    game_id         TEXT NOT NULL,
    result_token    TEXT UNIQUE NOT NULL,
    outcome         TEXT,
    coins_awarded   INTEGER NOT NULL DEFAULT 0,
    xp_awarded      INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_leaderboard ON users(level DESC, xp DESC);
CREATE INDEX IF NOT EXISTS idx_coin_tx_user ON coin_transactions(username);
CREATE INDEX IF NOT EXISTS idx_game_results_user ON game_results(username);
CREATE INDEX IF NOT EXISTS idx_game_sessions_user ON game_sessions(username);
CREATE TABLE IF NOT EXISTS multiplayer_rooms (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    room_code       TEXT UNIQUE NOT NULL,
    game_id         TEXT NOT NULL,
    host_username   TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'waiting',
    max_players     INTEGER NOT NULL DEFAULT 2,
    state_json      TEXT NOT NULL DEFAULT '{}',
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS multiplayer_players (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id         INTEGER NOT NULL REFERENCES multiplayer_rooms(id),
    username        TEXT NOT NULL,
    seat            INTEGER NOT NULL,
    ready           INTEGER NOT NULL DEFAULT 0,
    connected       INTEGER NOT NULL DEFAULT 1,
    joined_at       TEXT NOT NULL,
    UNIQUE(room_id, username)
);

CREATE INDEX IF NOT EXISTS idx_inventory_user ON user_inventory(username);
CREATE INDEX IF NOT EXISTS idx_audit_log_admin ON admin_audit_log(admin_username);
CREATE INDEX IF NOT EXISTS idx_audit_log_target ON admin_audit_log(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_users_created ON users(account_creation_date);
CREATE INDEX IF NOT EXISTS idx_mp_players_room ON multiplayer_players(room_id);
CREATE INDEX IF NOT EXISTS idx_mp_players_user ON multiplayer_players(username);
CREATE INDEX IF NOT EXISTS idx_mp_rooms_status ON multiplayer_rooms(game_id, status);
"""

_initialized = False


def get_connection():
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    global _initialized
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        _migrate_legacy_json(conn)
        _migrate_schema_additions(conn)
        _bootstrap_owner(conn)
    finally:
        conn.close()
    _initialized = True


def ensure_db():
    if not _initialized:
        init_db()


def _migrate_schema_additions(conn):
    """
    Adds columns that didn't exist in earlier versions of this schema
    (role / suspended / suspend_reason / leaderboard_visible) to a
    users table that was already created before they existed. A brand
    new database gets them straight from CREATE TABLE above and this
    is a no-op; an existing one (like this project's) gets ALTERed.
    Safe to run every startup.
    """
    existing_cols = {row["name"] for row in conn.execute("PRAGMA table_info(users)")}
    additions = {
        "role": "TEXT NOT NULL DEFAULT 'user'",
        "suspended": "INTEGER NOT NULL DEFAULT 0",
        "suspend_reason": "TEXT",
        "leaderboard_visible": "INTEGER NOT NULL DEFAULT 1",
    }
    changed = False
    for col, decl in additions.items():
        if col not in existing_cols:
            conn.execute(f"ALTER TABLE users ADD COLUMN {col} {decl}")
            changed = True
    if changed:
        conn.commit()
        print("[db] added admin-panel columns to the existing users table")

    # The old pre-shop default stored the bare string "obsidian" for
    # profile_theme, which never matched any real theme -- equipping a
    # theme silently did nothing. Clear it to '' (the new, real default)
    # so existing accounts fall back to the site's normal look instead
    # of a stale value that looks intentional but isn't.
    stale = conn.execute(
        "UPDATE users SET profile_theme = '' WHERE profile_theme = 'obsidian'"
    )
    if stale.rowcount:
        conn.commit()
        print(f"[db] normalized {stale.rowcount} account(s) off the old stale 'obsidian' default")


def _bootstrap_owner(conn):
    """
    One-time bootstrap: if nobody holds the 'owner' role yet, promote
    the 'zoro' account (this project's own dev/test account, previously
    tagged "owner" in the old pre-database profile data) so there's a
    way into the admin panel at all after this update. Only fires when
    zero owners exist -- once someone is owner, this never touches
    roles again.
    """
    has_owner = conn.execute("SELECT 1 FROM users WHERE role = 'owner'").fetchone()
    if has_owner:
        return
    zoro = conn.execute("SELECT 1 FROM users WHERE username = 'zoro'").fetchone()
    if zoro:
        conn.execute("UPDATE users SET role = 'owner', is_admin = 1 WHERE username = 'zoro'")
        conn.commit()
        print("[db] bootstrapped 'zoro' as the initial owner (no owner existed yet)")


def _migrate_legacy_json(conn):
    """
    One-time import of the old JSON-file storage (database/accounts.json +
    profiles/<username>.json) into the users table, so existing accounts
    survive the move to SQLite. Safe to call on every startup: it only
    inserts usernames that aren't already in the table.
    """
    accounts_path = os.path.join(DATABASE_DIR, "accounts.json")
    profiles_dir = os.path.join(BASE_DIR, "profiles")

    if not os.path.exists(accounts_path):
        return

    with open(accounts_path, "r", encoding="utf-8") as f:
        accounts = json.load(f)

    if not accounts:
        return

    migrated = 0
    for username, acct in accounts.items():
        existing = conn.execute(
            "SELECT 1 FROM users WHERE username = ?", (username,)
        ).fetchone()
        if existing:
            continue

        profile_path = os.path.join(profiles_dir, f"{username}.json")
        profile = {}
        if os.path.exists(profile_path):
            with open(profile_path, "r", encoding="utf-8") as pf:
                profile = json.load(pf)

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn.execute(
            """
            INSERT INTO users (
                username, uid, password_hash, is_admin,
                level, xp, coins,
                games_played, games_won, games_lost,
                current_streak, best_streak, favorite_game,
                biography, country,
                avatar, avatar_type, avatar_border,
                profile_banner, profile_theme, hub_version,
                achievements, badges, profile_unlocks,
                joined_date, account_creation_date, last_online, online_status
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                username,
                profile.get("uid") or f"NX-{username[:8].upper()}",
                acct.get("password", ""),
                1 if acct.get("admin") else 0,
                profile.get("level", 1),
                profile.get("xp", 0),
                profile.get("coins", 0),
                profile.get("games_played", 0),
                profile.get("games_won", 0),
                profile.get("games_lost", 0),
                profile.get("current_streak", 0),
                profile.get("best_streak", 0),
                profile.get("favorite_game"),
                profile.get("biography", "Welcome to my profile."),
                profile.get("country", "Global Space"),
                profile.get("avatar", "shadow-assassin"),
                profile.get("avatar_type", "builtin"),
                profile.get("avatar_border", "none"),
                profile.get("profile_banner", "default"),
                profile.get("profile_theme", ""),
                profile.get("hub_version", "v6"),
                json.dumps(profile.get("achievements", [])),
                json.dumps(profile.get("badges", ["Member"])),
                json.dumps(profile.get("profile_unlocks", [])),
                profile.get("joined_date", now),
                profile.get("account_creation_date", now),
                profile.get("last_online", now),
                profile.get("online_status", "offline"),
            ),
        )
        migrated += 1

    conn.commit()
    if migrated:
        print(f"[db] migrated {migrated} legacy account(s) from JSON into SQLite")
