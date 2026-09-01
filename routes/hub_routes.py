from flask import (
    render_template,
    redirect,
    url_for,
    session
)

from app import app

from profiles import (
    get_profile,
    create_profile,
    save_profile,
    avatar_url,
    banner_url
)

from services.shop_service import theme_css_classes

from config import THEMES


def get_user_profile():

    username = session.get("username")

    if not username:
        return None

    profile = get_profile(username)

    if profile is None:
        profile = create_profile(username)

    return profile


@app.route("/hub")
def hub():

    if "username" not in session:
        return redirect(url_for("index"))

    profile = get_user_profile()

    return render_template(

        "hub_v6.html",

        profile=profile,

        avatar_src=avatar_url(profile),

        banner_src=banner_url(profile),

        theme_classes=theme_css_classes(profile.get("profile_theme")),

        themes=THEMES

    )


@app.route("/hubv6")
def hub_v6():

    return redirect(url_for("hub"))