from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session
)

from app import app

from security.account_manager import (
    create_account,
    login_account,
    account_exists
)

from profiles import (
    create_profile,
    get_profile
)


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        username = request.form.get("username", "").strip()

        password = request.form.get("password", "").strip()

        action = request.form.get("action")

        if not username or not password:

            return render_template(
                "auth.html",
                error="Fill every field."
            )

        if action == "register":

            if account_exists(username):

                return render_template(
                    "auth.html",
                    error="Username already exists."
                )

            create_account(username, password)

            if get_profile(username) is None:

                create_profile(username)

            session["username"] = username

            return redirect(url_for("hub"))

        if action == "login":

            if not account_exists(username):

                return render_template(
                    "auth.html",
                    error="Account doesn't exist."
                )

            if not login_account(username, password):

                return render_template(
                    "auth.html",
                    error="Wrong password."
                )

            session["username"] = username

            return redirect(url_for("hub"))

    return render_template("auth.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("index"))