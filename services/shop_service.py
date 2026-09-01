# services/shop_service.py

# ============================================================
# ZORO HUB — SHOP SERVICE
# ============================================================
#
# Real prices (tiered per the economy spec), real ownership via
# user_inventory, real coin deduction via the same coin_transactions
# ledger the game-reward pipeline uses. Nothing here is free anymore.
#
# One known gap, worth knowing about rather than hiding: the shop
# catalog lists 13 individually named themes, but the theme-rendering
# system (static/js/themes_manager.js) currently only styles by RARITY
# TIER (6 look-and-feels: common/uncommon/rare/epic/legendary/mythic),
# not by individual theme name. So right now, buying and equipping
# "Slate" vs "Ash" vs "Dusk" (all common) will look identical, even
# though they're separate purchasable items. The purchase/ownership/
# equip system below is fully real regardless -- this is specifically
# about visual distinctiveness between same-rarity themes, which is a
# design task (13 real palettes) more than a backend one.
# ============================================================


SHOP_ITEMS = [

    # ========================================================
    # AVATARS
    # ========================================================

    {
        "id": "avatar_zoro",
        "name": "Zoro",
        "category": "avatars",
        "description": "The classic Zoro Hub avatar.",
        "price": 800,
        "rarity": "common",
    },

    {
        "id": "avatar_shadow",
        "name": "Shadow",
        "category": "avatars",
        "description": "A darker profile identity.",
        "price": 8000,
        "rarity": "rare",
    },

    {
        "id": "avatar_samurai",
        "name": "Samurai",
        "category": "avatars",
        "description": "A legendary warrior avatar.",
        "price": 22000,
        "rarity": "epic",
    },


    # ========================================================
    # BANNERS
    # ========================================================

    {
        "id": "banner_sunset",
        "name": "Sunset",
        "category": "banners",
        "description": "A warm atmospheric profile banner.",
        "price": 600,
        "rarity": "common",
    },

    {
        "id": "banner_void",
        "name": "Void",
        "category": "banners",
        "description": "A deep space-inspired profile banner.",
        "price": 20000,
        "rarity": "epic",
    },

    {
        "id": "banner_legend",
        "name": "Legend",
        "category": "banners",
        "description": "A banner for legendary players.",
        "price": 50000,
        "rarity": "legendary",
    },


    # ========================================================
    # COMMON THEMES
    # ========================================================

    {
        "id": "theme_slate",
        "name": "Slate",
        "category": "themes",
        "description": "A restrained charcoal interface.",
        "price": 750,
        "rarity": "common",
        "theme_class": "theme-slate",
    },

    {
        "id": "theme_ash",
        "name": "Ash",
        "category": "themes",
        "description": "A soft monochrome interface.",
        "price": 750,
        "rarity": "common",
        "theme_class": "theme-ash",
    },

    {
        "id": "theme_dusk",
        "name": "Dusk",
        "category": "themes",
        "description": "A quiet dark evening palette.",
        "price": 900,
        "rarity": "common",
        "theme_class": "theme-dusk",
    },


    # ========================================================
    # UNCOMMON THEMES
    # ========================================================

    {
        "id": "theme_forest",
        "name": "Forest",
        "category": "themes",
        "description": "A deep natural green palette.",
        "price": 2500,
        "rarity": "uncommon",
        "theme_class": "theme-forest",
    },

    {
        "id": "theme_ocean",
        "name": "Ocean",
        "category": "themes",
        "description": "A cool navy and blue interface.",
        "price": 2800,
        "rarity": "uncommon",
        "theme_class": "theme-ocean",
    },

    {
        "id": "theme_ember",
        "name": "Ember",
        "category": "themes",
        "description": "A restrained warm ember palette.",
        "price": 3200,
        "rarity": "uncommon",
        "theme_class": "theme-ember",
    },


    # ========================================================
    # RARE THEMES
    # ========================================================

    {
        "id": "theme_midnight",
        "name": "Midnight",
        "category": "themes",
        "description": "A polished blue-black interface.",
        "price": 7000,
        "rarity": "rare",
        "theme_class": "theme-midnight",
    },

    {
        "id": "theme_ivory",
        "name": "Ivory",
        "category": "themes",
        "description": "A refined dark ivory palette.",
        "price": 8500,
        "rarity": "rare",
        "theme_class": "theme-ivory",
    },

    {
        "id": "theme_crimson",
        "name": "Crimson",
        "category": "themes",
        "description": "A deep red and charcoal interface.",
        "price": 9500,
        "rarity": "rare",
        "theme_class": "theme-crimson",
    },


    # ========================================================
    # EPIC THEMES
    # ========================================================

    {
        "id": "theme_royal",
        "name": "Royal",
        "category": "themes",
        "description": "A rich violet interface with muted gold.",
        "price": 18000,
        "rarity": "epic",
        "theme_class": "theme-royal",
    },

    {
        "id": "theme_obsidian",
        "name": "Obsidian",
        "category": "themes",
        "description": "A deep almost-black interface.",
        "price": 20000,
        "rarity": "epic",
        "theme_class": "theme-obsidian",
    },

    {
        "id": "theme_aurora",
        "name": "Aurora",
        "category": "themes",
        "description": "A subtle atmospheric night palette.",
        "price": 24000,
        "rarity": "epic",
        "theme_class": "theme-aurora",
    },


    # ========================================================
    # LEGENDARY
    # ========================================================

    {
        "id": "theme_imperial",
        "name": "Imperial",
        "category": "themes",
        "description": "A luxurious charcoal and champagne palette.",
        "price": 45000,
        "rarity": "legendary",
        "theme_class": "theme-imperial",
    },


    # ========================================================
    # MYTHIC
    # ========================================================

    {
        "id": "theme_eclipse",
        "name": "Eclipse",
        "category": "themes",
        "description": "A rare celestial-inspired interface.",
        "price": 95000,
        "rarity": "mythic",
        "theme_class": "theme-eclipse",
    },
]


# ============================================================
# PUBLIC FUNCTIONS
# ============================================================

def get_all_items():
    """Return all shop items."""
    return [item.copy() for item in SHOP_ITEMS]


def get_item(item_id):
    """Return one shop item by ID."""
    for item in SHOP_ITEMS:
        if item["id"] == item_id:
            return item.copy()

    return None


def get_items_by_category(category):
    """Return all items belonging to a category."""
    category = category.strip().lower()

    return [
        item.copy()
        for item in SHOP_ITEMS
        if item.get("category", "").lower() == category
    ]


def get_categories():
    """Return all unique shop categories."""
    categories = []

    for item in SHOP_ITEMS:
        category = item.get("category")

        if category and category not in categories:
            categories.append(category)

    return categories


def get_item_count():
    """Return the total number of shop items."""
    return len(SHOP_ITEMS)


def is_item_free(item_id):
    """Return True when an item is currently free."""
    item = get_item(item_id)

    if item is None:
        return False

    return item.get("price", 0) == 0

# ============================================================
# OWNERSHIP / PURCHASE / EQUIP
# ============================================================
# Real from here down: coins are checked and deducted server-side,
# ownership is a real row in user_inventory, and equipping something
# you don't own is not possible through this code path -- there's no
# client-trusted branch that skips the ownership check.

class PurchaseError(Exception):
    pass


def get_user_inventory(username):
    from security.database import get_connection, ensure_db
    ensure_db()
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT item_id, acquired_at FROM user_inventory WHERE username = ?", (username,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def owns_item(username, item_id):
    owned_ids = {row["item_id"] for row in get_user_inventory(username)}
    return item_id in owned_ids


def purchase_item(username, item_id):
    """The only real path to owning a shop item."""
    from security.database import get_connection, ensure_db
    from profiles import get_profile, save_profile
    from datetime import datetime

    item = get_item(item_id)
    if item is None:
        raise PurchaseError("no such item")

    ensure_db()
    conn = get_connection()
    try:
        already_owned = conn.execute(
            "SELECT 1 FROM user_inventory WHERE username = ? AND item_id = ?",
            (username, item_id),
        ).fetchone()
        if already_owned:
            raise PurchaseError("already owned")

        profile = get_profile(username)
        if profile is None:
            raise PurchaseError("no such user")

        price = item["price"]
        if profile["coins"] < price:
            raise PurchaseError(f"insufficient coins: need {price}, have {profile['coins']}")

        balance_before = profile["coins"]
        profile["coins"] = balance_before - price
        save_profile(username, profile)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO user_inventory (username, item_id, acquired_at) VALUES (?, ?, ?)",
            (username, item_id, now),
        )
        conn.execute(
            """INSERT INTO coin_transactions
               (username, type, amount, balance_before, balance_after, source, related_item, created_at)
               VALUES (?, 'SHOP_PURCHASE', ?, ?, ?, ?, ?, ?)""",
            (username, -price, balance_before, balance_before - price, "shop", item_id, now),
        )
        conn.commit()
        return {"item": item, "new_balance": balance_before - price}
    finally:
        conn.close()


# Which profile column each category equips into. Everything here reuses
# the same columns the rest of the profile system already reads from
# (avatar_url()/banner_url() etc.) -- equipping a shop item and equipping
# a builtin avatar update the exact same source of truth.
EQUIP_SLOT_BY_CATEGORY = {
    "avatars": "avatar",
    "banners": "profile_banner",
    "themes": "profile_theme",
}


def theme_css_classes(profile_theme_value):
    """
    The single source of truth for turning a stored profile_theme value
    (e.g. "theme_slate", an item_id) into the actual CSS classes that
    make the equipped theme visually apply -- both the rarity base
    palette (bg/surface/text/border) AND the specific theme's accent
    override, hyphenated to match the real CSS selectors. Anything
    unrecognized (empty, a stale/legacy value) safely falls back to
    "", which just uses hub_v6.css's own built-in default colors.

    Every page that shows the equipped theme should call this rather
    than rendering profile['profile_theme'] directly -- that was the
    actual bug: the stored item_id ("theme_slate") never matched any
    CSS class ("theme-slate"), and the rarity class was never applied
    at all, so equipping a theme silently did nothing.
    """
    if not profile_theme_value:
        return ""
    item = get_item(profile_theme_value)
    if item is None or item.get("category") != "themes":
        return ""
    slug = profile_theme_value.replace("_", "-")
    rarity = (item.get("rarity") or "").lower()
    if not rarity:
        return slug
    return f"theme-{rarity} {slug}"


def equip_item(username, item_id):
    from profiles import get_profile, save_profile

    item = get_item(item_id)
    if item is None:
        raise PurchaseError("no such item")
    if not owns_item(username, item_id):
        raise PurchaseError("item not owned")

    slot = EQUIP_SLOT_BY_CATEGORY.get(item["category"])
    if slot is None:
        raise PurchaseError(f"category '{item['category']}' isn't equippable yet")

    profile = get_profile(username)
    if profile is None:
        raise PurchaseError("no such user")

    profile[slot] = item_id
    if slot == "avatar":
        profile["avatar_type"] = "shop"
    save_profile(username, profile)
    return profile
