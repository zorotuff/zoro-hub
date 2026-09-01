from services.multiplayer_games import tic_tac_toe

GAME_REGISTRY = {
    "tic_tac_toe_mp": tic_tac_toe,
}


def get_game_module(game_id):
    module = GAME_REGISTRY.get(game_id)
    if module is None:
        raise ValueError(f"no multiplayer game registered for {game_id!r}")
    return module
