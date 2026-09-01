from profiles import (
    save_profile,
    add_xp,
    evaluate_achievements,
    evaluate_badges
)

# ==========================================
# GIVE REWARDS
# ==========================================

def reward_player(profile,
                  *,
                  xp=0,
                  coins=0,
                  win=False,
                  loss=False,
                  draw=False):

    profile["games_played"] = profile.get("games_played", 0) + 1

    if win:

        profile["games_won"] = profile.get("games_won", 0) + 1

        profile["current_streak"] = profile.get("current_streak", 0) + 1

        if profile["current_streak"] > profile.get("best_streak", 0):

            profile["best_streak"] = profile["current_streak"]

    elif loss:

        profile["games_lost"] = profile.get("games_lost", 0) + 1

        profile["current_streak"] = 0

    elif draw:

        pass

    profile["coins"] = profile.get("coins", 0) + coins

    profile = add_xp(profile, xp)

    profile = evaluate_achievements(profile)

    profile = evaluate_badges(profile)

    save_profile(profile["username"], profile)

    return profile