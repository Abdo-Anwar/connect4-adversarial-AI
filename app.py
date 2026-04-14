"""Flask web application for Connect-4 with adversarial AI."""

import math
import json

from flask import Flask, jsonify, render_template, request

from ai import alpha_beta, expectimax, minimax
from game import (
    AI_PIECE,
    PLAYER_PIECE,
    check_win,
    create_board,
    get_valid_locations,
    is_draw,
    make_move,
)

app = Flask(__name__)


def _sanitize_tree(node):
    """Replace inf / -inf / None with JSON-safe values."""
    if node is None:
        return None
    sanitized = dict(node)
    if sanitized.get("score") is None:
        sanitized["score"] = "pruned"
    elif isinstance(sanitized["score"], float):
        if math.isinf(sanitized["score"]):
            sanitized["score"] = 1e9 if sanitized["score"] > 0 else -1e9
    if "alpha" in sanitized and isinstance(sanitized["alpha"], float):
        if math.isinf(sanitized["alpha"]):
            sanitized["alpha"] = 1e9 if sanitized["alpha"] > 0 else -1e9
    if "beta" in sanitized and isinstance(sanitized["beta"], float):
        if math.isinf(sanitized["beta"]):
            sanitized["beta"] = 1e9 if sanitized["beta"] > 0 else -1e9
    sanitized["children"] = [
        _sanitize_tree(c) for c in sanitized.get("children", [])
    ]
    return sanitized


@app.route("/")
def index():
    """Render the main game page."""
    return render_template("index.html")


@app.route("/api/move", methods=["POST"])
def api_move():
    """Accept a board state and AI parameters, return the AI move and tree."""
    data = request.get_json(force=True)
    board = data.get("board")
    algorithm = data.get("algorithm", "minimax")
    depth = int(data.get("depth", 4))

    # Clamp depth to a safe range
    depth = max(1, min(depth, 7))

    if board is None:
        return jsonify({"error": "Missing board"}), 400

    valid = get_valid_locations(board)
    if not valid:
        return jsonify({"error": "No valid moves"}), 400

    tree = None
    if algorithm == "minimax":
        col, score, tree = minimax(board, depth, True, record_tree=True)
    elif algorithm == "alphabeta":
        col, score, tree = alpha_beta(
            board, depth, -math.inf, math.inf, True, record_tree=True
        )
    elif algorithm == "expectimax":
        col, score, tree = expectimax(board, depth, True, record_tree=True)
    else:
        return jsonify({"error": f"Unknown algorithm: {algorithm}"}), 400

    new_board = make_move(board, col, AI_PIECE)
    winner = None
    if check_win(new_board, AI_PIECE):
        winner = "ai"
    elif is_draw(new_board):
        winner = "draw"

    safe_tree = _sanitize_tree(tree)

    return jsonify({
        "col": col,
        "board": new_board,
        "score": score if not math.isinf(score) else (1e9 if score > 0 else -1e9),
        "winner": winner,
        "tree": safe_tree,
    })


@app.route("/api/check", methods=["POST"])
def api_check():
    """Check if a player move results in a win or draw."""
    data = request.get_json(force=True)
    board = data.get("board")
    col = data.get("col")

    if board is None or col is None:
        return jsonify({"error": "Missing board or col"}), 400

    new_board = make_move(board, col, PLAYER_PIECE)
    if new_board is None:
        return jsonify({"error": "Invalid move"}), 400

    winner = None
    if check_win(new_board, PLAYER_PIECE):
        winner = "player"
    elif is_draw(new_board):
        winner = "draw"

    return jsonify({
        "board": new_board,
        "winner": winner,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
