# routes/shop_route.py

from flask import Blueprint, render_template, jsonify, session, request

from services.shop_service import (
    get_all_items,
    get_item,
    get_items_by_category,
    get_categories,
    get_item_count,
    get_user_inventory,
    owns_item,
    purchase_item,
    equip_item,
    theme_css_classes,
    PurchaseError,
)


# ============================================================
# SHOP BLUEPRINT
# ============================================================

shop_bp = Blueprint(
    "zoro_shop",
    __name__,
    url_prefix="/shop"
)


# ============================================================
# SHOP PAGE
# ============================================================

@shop_bp.route("/")
def shop():
    from flask import session, redirect, url_for
    from profiles import get_profile

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_profile(session["username"])
    owned_ids = [row["item_id"] for row in get_user_inventory(session["username"])]
    equipped = {
        "avatars": profile.get("avatar") if profile.get("avatar_type") == "shop" else None,
        "banners": profile.get("profile_banner") if str(profile.get("profile_banner", "")).startswith("banner_") else None,
        "theme": profile.get("profile_theme") if str(profile.get("profile_theme", "")).startswith("theme_") else None,
        "themeClass": theme_css_classes(profile.get("profile_theme")),
    }

    return render_template(
        "shop.html",
        initial_owned=owned_ids,
        initial_equipped=equipped,
        initial_coins=profile.get("coins", 0),
    )


# ============================================================
# SHOP API
# ============================================================

@shop_bp.route("/api/items")
def shop_items():
    return jsonify({
        "success": True,
        "items": get_all_items(),
        "count": get_item_count()
    })


@shop_bp.route("/api/items/<item_id>")
def shop_item(item_id):
    item = get_item(item_id)

    if item is None:
        return jsonify({
            "success": False,
            "error": "Item not found"
        }), 404

    return jsonify({
        "success": True,
        "item": item
    })


# ============================================================
# CATEGORY API
# ============================================================

@shop_bp.route("/api/category/<category>")
def shop_category(category):
    items = get_items_by_category(category)

    return jsonify({
        "success": True,
        "category": category,
        "items": items,
        "count": len(items)
    })


# ============================================================
# CATEGORIES API
# ============================================================

@shop_bp.route("/api/categories")
def shop_categories():
    return jsonify({
        "success": True,
        "categories": get_categories()
    })


# ============================================================
# OWNERSHIP / PURCHASE / EQUIP
# ============================================================
# Every route below requires a real session -- no username is ever
# taken from the request body. The server decides who "you" are.

@shop_bp.route("/api/inventory")
def my_inventory():
    if "username" not in session:
        return jsonify({"success": False, "error": "not_authenticated"}), 401

    owned = get_user_inventory(session["username"])
    return jsonify({"success": True, "inventory": owned})


@shop_bp.route("/api/purchase", methods=["POST"])
def purchase():
    if "username" not in session:
        return jsonify({"success": False, "error": "not_authenticated"}), 401

    data = request.get_json(silent=True) or {}
    item_id = data.get("item_id")
    if not isinstance(item_id, str) or not item_id:
        return jsonify({"success": False, "error": "invalid_input", "detail": "item_id is required"}), 400

    try:
        result = purchase_item(session["username"], item_id)
    except PurchaseError as e:
        detail = str(e)
        status = 409 if "already owned" in detail else (402 if "insufficient" in detail else 400)
        return jsonify({"success": False, "error": "purchase_failed", "detail": detail}), status

    return jsonify({
        "success": True,
        "item": result["item"],
        "new_balance": result["new_balance"],
    })


@shop_bp.route("/api/equip", methods=["POST"])
def equip():
    if "username" not in session:
        return jsonify({"success": False, "error": "not_authenticated"}), 401

    data = request.get_json(silent=True) or {}
    item_id = data.get("item_id")
    if not isinstance(item_id, str) or not item_id:
        return jsonify({"success": False, "error": "invalid_input", "detail": "item_id is required"}), 400

    try:
        profile = equip_item(session["username"], item_id)
    except PurchaseError as e:
        detail = str(e)
        status = 403 if "not owned" in detail else 400
        return jsonify({"success": False, "error": "equip_failed", "detail": detail}), status

    return jsonify({"success": True, "profile": {
        "avatar": profile["avatar"], "avatar_type": profile["avatar_type"],
        "profile_banner": profile["profile_banner"], "profile_theme": profile["profile_theme"],
    }})