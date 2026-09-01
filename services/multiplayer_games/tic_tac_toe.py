"""
Multiplayer Tic-Tac-Toe. Every move is validated server-side -- a
client claiming "I won" with no legitimate board state is impossible;
the win is only ever set by _check_winner() acting on the real board
this module maintains.
"""

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]


def initial_state(usernames):
    if len(usernames) != 2:
        raise ValueError("tic_tac_toe_mp needs exactly 2 players")
    return {
        "board": [None] * 9,
        "turn": usernames[0],
        "players": {usernames[0]: "X", usernames[1]: "O"},
        "game_over": False,
        "winner": None,
        "reward_tiers": {},
    }


def apply_move(state, username, move, players):
    if state.get("game_over"):
        raise ValueError("this game is already over")
    if username not in state["players"]:
        raise ValueError("you're not a player in this game")
    if state["turn"] != username:
        raise ValueError("it's not your turn")

    position = move.get("position")
    if not isinstance(position, int) or not (0 <= position <= 8):
        raise ValueError("invalid board position")
    if state["board"][position] is not None:
        raise ValueError("that square is already taken")

    symbol = state["players"][username]
    state["board"][position] = symbol

    winner_symbol = _check_winner(state["board"])
    if winner_symbol:
        winner = next(u for u, s in state["players"].items() if s == winner_symbol)
        loser = next(u for u in state["players"] if u != winner)
        state["game_over"] = True
        state["winner"] = winner
        state["reward_tiers"] = {winner: "winner", loser: "participation"}
    elif all(cell is not None for cell in state["board"]):
        state["game_over"] = True
        state["winner"] = None
        state["reward_tiers"] = {u: "good" for u in state["players"]}
    else:
        state["turn"] = next(u for u in state["players"] if u != username)

    return state


def _check_winner(board):
    for a, b, c in WIN_LINES:
        if board[a] is not None and board[a] == board[b] == board[c]:
            return board[a]
    return None
