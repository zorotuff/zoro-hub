import json
import os

PROFILE_FOLDER = "profiles"


def get_profile(username):

    path = os.path.join(PROFILE_FOLDER, f"{username}.json")

    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(profile):

    path = os.path.join(
        PROFILE_FOLDER,
        f"{profile['username']}.json"
    )

    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=4)