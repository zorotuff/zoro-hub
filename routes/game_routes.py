from flask import render_template, redirect, url_for, session
from app import app
from services.profile_service import get_profile
from services.shop_service import theme_css_classes


@app.route("/games")
def games():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_profile(session["username"])

    return render_template(
        "games.html",
        profile=profile,
        theme_classes=theme_css_classes(profile.get("profile_theme")),
    )


@app.route("/tic_tac_toe")
def tic_tac_toe():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_profile(session["username"])

    return render_template(
        "tictactoe.html",
        profile=profile
    )


from flask import render_template, redirect, url_for, session, request

@app.route("/kitty_dash")
def kitty_dash():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_profile(session["username"])

    user_agent = request.user_agent.string.lower()

    if "android" in user_agent or "iphone" in user_agent:
        return render_template(
            "kitty_dash_mobile.html",
            profile=profile
        )

    return render_template(
        "kitty_dash.html",
        profile=profile
    )

@app.route("/chess")
def chess():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_profile(session["username"])

    return render_template(
        "chess.html",
        profile=profile
    )

from flask import request

@app.route("/space_shooter")
def space_shooter():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_profile(session["username"])

    ua = request.headers.get("User-Agent", "").lower()

    if "android" in ua or "iphone" in ua or "ipad" in ua:
        return render_template(
            "space_shooter_mobile.html",
            profile=profile
        )

    return render_template(
        "space_shooter.html",
        profile=profile
    )
