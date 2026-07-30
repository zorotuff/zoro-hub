import os

print("GTN ROUTES FILE:")
print(os.path.abspath(__file__))

from flask import render_template, redirect, url_for, session
from app import app
print("GTN ROUTES LOADED")
from services.profile_service import get_profile


@app.route("/games")
def games():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_profile(session["username"])

    return render_template(
        "games.html",
        profile=profile
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


@app.route("/kitty_dash")
def kitty_dash():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_profile(session["username"])

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


@app.route("/guess_the_number")
def guess_the_number():

    if "username" not in session:
        return redirect(url_for("index"))

    return render_template("gtn_difficulty.html")

from flask import *

import random

from app import app

@app.route("/gtn")
def gtn_difficulty():

    if "username" not in session:
        return redirect(url_for("index"))

    return render_template("gtn_difficulty.html")

@app.route("/set_difficulty/<level>")
def set_difficulty(level):

    session["difficulty"] = level

    session["secret"] = random.randint(1,200)

    if level=="easy":
        session["attempts"]=15

    elif level=="medium":
        session["attempts"]=10

    elif level=="hard":
        session["attempts"]=7

    return redirect("/gtn/game")

@app.route("/gtn/game")
def gtn_game():

    return render_template(

        "gtn_game.html",

        difficulty=session.get("difficulty"),

        attempts=session.get("attempts")

    )

@app.route("/gtn/guess", methods=["POST"])
def gtn_guess():

    guess = int(request.form["guess"])

    secret = session["secret"]

    attempts = session["attempts"] - 1

    session["attempts"] = attempts

    message = ""

    game_over = False

    if guess == secret:

        message = "🎉 Correct!"

        game_over = True

    elif attempts <= 0:

        message = f"💀 You Lost! Number was {secret}"

        game_over = True

    elif guess < secret:

        message = "⬆ Too Low"

    else:

        message = "⬇ Too High"

    return render_template(

        "gtn_game.html",

        difficulty=session["difficulty"],

        attempts=attempts,

        message=message,

        game_over=game_over

    )