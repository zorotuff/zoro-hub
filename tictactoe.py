# tictactoe_ai.py
"""
Tic Tac Toe game engine + Minimax AI.
Pure logic module — no Flask/session code here, so it can be unit-tested
or reused elsewhere.
"""

import math
import random

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # cols
    (0, 4, 8), (2, 4, 6),              # diagonals
]


def check_winner(board):
    """
    Returns (winner, line) where winner is 'X', 'O', 'draw', or None (game ongoing).
    line is the winning (a, b, c) tuple, or None.
    """
    for a, b, c in WIN_LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a], (a, b, c)

    if " " not in board:
        return "draw", None

    return None, None


def _minimax(board, depth, is_maximizing, ai_symbol, human_symbol, alpha, beta):
    winner, _ = check_winner(board)

    if winner == ai_symbol:
        return 10 - depth
    if winner == human_symbol:
        return depth - 10
    if winner == "draw":
        return 0

    if is_maximizing:
        best = -math.inf
        for i in range(9):
            if board[i] == " ":
                board[i] = ai_symbol
                score = _minimax(board, depth + 1, False, ai_symbol, human_symbol, alpha, beta)
                board[i] = " "
                best = max(best, score)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
        return best
    else:
        best = math.inf
        for i in range(9):
            if board[i] == " ":
                board[i] = human_symbol
                score = _minimax(board, depth + 1, True, ai_symbol, human_symbol, alpha, beta)
                board[i] = " "
                best = min(best, score)
                beta = min(beta, best)
                if beta <= alpha:
                    break
        return best


def _best_move(board, ai_symbol, human_symbol):
    """Unbeatable move via minimax + alpha-beta pruning."""
    best_score = -math.inf
    move = None

    # Slight randomization among equally-good moves so the AI doesn't
    # always play the exact same opening.
    candidates = [i for i in range(9) if board[i] == " "]
    random.shuffle(candidates)

    for i in candidates:
        board[i] = ai_symbol
        score = _minimax(board, 0, False, ai_symbol, human_symbol, -math.inf, math.inf)
        board[i] = " "
        if score > best_score:
            best_score = score
            move = i

    return move


def _random_move(board):
    empties = [i for i, v in enumerate(board) if v == " "]
    return random.choice(empties) if empties else None


def get_ai_move(board, ai_symbol, human_symbol, difficulty="hard"):
    """
    difficulty: "easy" | "medium" | "hard"
      easy   -> mostly random, occasionally smart (beatable, good for beginners)
      medium -> a coin-flip between random and optimal
      hard   -> always optimal (unbeatable — best case is a draw)
    """
    empties = [i for i, v in enumerate(board) if v == " "]
    if not empties:
        return None

    if difficulty == "easy":
        if random.random() < 0.75:
            return _random_move(board)
        return _best_move(board, ai_symbol, human_symbol)

    if difficulty == "medium":
        if random.random() < 0.4:
            return _random_move(board)
        return _best_move(board, ai_symbol, human_symbol)

    # hard / unbeatable
    return _best_move(board, ai_symbol, human_symbol)