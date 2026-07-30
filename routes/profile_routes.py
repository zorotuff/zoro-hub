from flask import render_template, session, redirect, url_for
from app import app
from services.profile_service import get_profile


@app.route("/profile")
def profile():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_profile(session["username"])

    return render_template(
        "profile.html",
        profile=profile
    )


@app.route("/leaderboard")
def leaderboard():
    return "Leaderboard (Coming Soon)"


@app.route("/settings")
def settings():
    return "Settings (Coming Soon)"


@app.route("/achievements")
def achievements():
    return "Achievements (Coming Soon)"