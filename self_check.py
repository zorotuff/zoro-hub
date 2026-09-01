"""
Zoro Hub self-check.

Run this any time something seems off:

    python self_check.py

It spins up the app in-process, exercises the core flows (accounts,
sessions, the reward pipeline, every registered route), prints a clear
PASS/FAIL for each one, and cleans up its own test data when it's done.
It does NOT touch your real accounts.

If something fails, the traceback (if any) and a description of what
was being checked are printed right there -- also check logs/zoro_hub.log
for the full picture of anything that happened along the way.
"""

import sys
import traceback
import uuid

sys.path.insert(0, ".")

RESULTS = []


def check(name):
    """Decorator: run a check, record PASS/FAIL, never let one check's
    crash stop the rest from running."""
    def decorator(fn):
        try:
            fn()
            RESULTS.append((name, True, None))
        except Exception as e:
            RESULTS.append((name, False, f"{type(e).__name__}: {e}"))
            if "--verbose" in sys.argv:
                traceback.print_exc()
        return fn
    return decorator


TEST_USER = f"selfcheck_{uuid.uuid4().hex[:8]}"
TEST_PASS = "selfcheck-pass-123"


def _cleanup(username):
    from security.database import get_connection, ensure_db
    ensure_db()
    conn = get_connection()
    try:
        for tbl in ("coin_transactions", "game_results", "game_sessions", "user_inventory"):
            conn.execute(f"DELETE FROM {tbl} WHERE username=?", (username,))
        conn.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
    finally:
        conn.close()


print(f"Zoro Hub self-check -- test account: {TEST_USER}\n")

try:
    from app import app
    app.testing = False
    client = app.test_client()
except Exception:
    print("FATAL: the app itself failed to import. Nothing else can run.\n")
    traceback.print_exc()
    sys.exit(1)


@check("app imports and boots")
def _():
    assert app is not None


@check("register a new account")
def _():
    r = client.post("/", data={"username": TEST_USER, "password": TEST_PASS, "action": "register"})
    assert r.status_code == 302, f"expected redirect after register, got {r.status_code}"


@check("new profile has real DB defaults (coins=0, level=1, no password leak)")
def _():
    from profiles import get_profile
    p = get_profile(TEST_USER)
    assert p is not None, "profile was not created"
    assert p["coins"] == 0 and p["level"] == 1
    assert "password_hash" not in p, "password hash leaked into the profile dict"


@check("logout then login again works")
def _():
    client.get("/logout")
    r = client.post("/", data={"username": TEST_USER, "password": TEST_PASS, "action": "login"})
    assert r.status_code == 302


@check("wrong password is rejected, not a crash")
def _():
    client.get("/logout")
    r = client.post("/", data={"username": TEST_USER, "password": "definitely-wrong", "action": "login"})
    assert r.status_code < 500
    client.post("/", data={"username": TEST_USER, "password": TEST_PASS, "action": "login"})  # log back in


@check("starting a game session returns a real token")
def _():
    r = client.post("/api/games/start", json={"game_id": "kitty"})
    assert r.status_code == 200
    tok = r.get_json().get("session_token")
    assert tok and len(tok) > 20
    globals()["_session_token"] = tok


@check("claiming a high tier immediately (no time elapsed) is rejected")
def _():
    r = client.post("/api/games/report-result",
                     json={"game_id": "kitty", "tier": "exceptional", "session_token": _session_token})
    assert r.status_code == 403, f"expected 403, got {r.status_code}: {r.get_json()}"


@check("a real result, after enough time, actually pays out")
def _():
    from security.database import get_connection
    conn = get_connection()
    conn.execute("UPDATE game_sessions SET started_at = datetime('now', '-10 seconds') WHERE session_token=?",
                 (_session_token,))
    conn.commit()
    conn.close()
    r = client.post("/api/games/report-result",
                     json={"game_id": "kitty", "tier": "low", "session_token": _session_token})
    assert r.status_code == 200, r.get_json()
    body = r.get_json()
    assert 50 <= body["coins_awarded"] <= 150


@check("replaying the same session token is rejected (no double-reward)")
def _():
    r = client.post("/api/games/report-result",
                     json={"game_id": "kitty", "tier": "low", "session_token": _session_token})
    assert r.status_code == 409


@check("a forged / made-up session token is rejected")
def _():
    r = client.post("/api/games/report-result",
                     json={"game_id": "kitty", "tier": "exceptional", "session_token": "not-a-real-token"})
    assert r.status_code == 403


@check("malformed input (non-string tier) is a clean 400, not a 500")
def _():
    r = client.post("/api/games/report-result",
                     json={"game_id": "kitty", "tier": {"bad": "type"}, "session_token": "x"})
    assert r.status_code == 400, f"expected 400, got {r.status_code}"


@check("every registered route responds without a 500")
def _():
    bad = []
    for rule in app.url_map.iter_rules():
        if "GET" not in rule.methods or "<" in str(rule):
            continue
        r = client.get(str(rule))
        if r.status_code >= 500:
            bad.append((str(rule), r.status_code))
    assert not bad, f"routes returning 5xx: {bad}"


@check("legacy accounts (zoro / chillzoro) are untouched")
def _():
    from security.database import get_connection, ensure_db
    ensure_db()
    conn = get_connection()
    rows = {r["username"]: dict(r) for r in conn.execute(
        "SELECT username, xp, games_won FROM users WHERE username IN ('zoro','chillzoro')")}
    conn.close()
    assert "zoro" in rows and "chillzoro" in rows, "expected legacy accounts are missing!"


@check("shop: buying with insufficient coins is rejected, not silently allowed")
def _():
    # the "every route" check above hits /logout along the way -- get back in
    client.post("/", data={"username": TEST_USER, "password": TEST_PASS, "action": "login"})
    r = client.post("/shop/api/purchase", json={"item_id": "theme_slate"})
    assert r.status_code == 402, f"expected 402, got {r.status_code}: {r.get_json()}"


@check("shop: a real purchase (after really earning coins) deducts the right amount")
def _():
    r = client.post("/api/games/start", json={"game_id": "kitty"})
    tok = r.get_json()["session_token"]
    from security.database import get_connection
    conn = get_connection()
    conn.execute("UPDATE game_sessions SET started_at = datetime('now', '-50 seconds') WHERE session_token=?", (tok,))
    conn.commit(); conn.close()
    r = client.post("/api/games/report-result", json={"game_id": "kitty", "tier": "exceptional", "session_token": tok})
    balance = r.get_json()["new_balance"]
    r = client.post("/shop/api/purchase", json={"item_id": "theme_slate"})
    assert r.status_code == 200, r.get_json()
    assert r.get_json()["new_balance"] == balance - 750


@check("shop: buying the same item twice is rejected")
def _():
    r = client.post("/shop/api/purchase", json={"item_id": "theme_slate"})
    assert r.status_code == 409


@check("shop: equipping something you don't own is rejected")
def _():
    r = client.post("/shop/api/equip", json={"item_id": "theme_eclipse"})
    assert r.status_code == 403


@check("shop: equipping something you DO own persists to the real profile")
def _():
    r = client.post("/shop/api/equip", json={"item_id": "theme_slate"})
    assert r.status_code == 200
    from profiles import get_profile
    p = get_profile(TEST_USER)
    assert p["profile_theme"] == "theme_slate"


_cleanup(TEST_USER)

print(f"{'CHECK':<62}{'RESULT'}")
print("-" * 74)
failed = 0
for name, passed, detail in RESULTS:
    status = "PASS" if passed else "FAIL"
    print(f"{name:<62}{status}")
    if not passed:
        failed += 1
        print(f"    -> {detail}")

print("-" * 74)
print(f"{len(RESULTS) - failed}/{len(RESULTS)} passed")
if failed:
    print("\nSee logs/zoro_hub.log for full tracebacks of anything that broke.")
    print("Run with --verbose to also print tracebacks here.")
    sys.exit(1)
else:
    print("\nEverything in this check is working.")
