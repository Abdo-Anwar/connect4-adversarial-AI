"""Adversarial AI strategies for Connect-4.

Implements Minimax, Alpha-Beta pruning, and Expectimax algorithms
with search-tree recording for real-time visualization.
"""

import math
import random

from game import (
    AI_PIECE,
    PLAYER_PIECE,
    check_win,
    get_valid_locations,
    is_terminal_node,
    make_move,
    score_position,
)


def _new_node(col, score, node_type, depth, alpha=None, beta=None, children=None):
    """Create a tree node dictionary for visualization."""
    node = {
        "col": col,
        "score": score,
        "type": node_type,
        "depth": depth,
        "children": children or [],
    }
    if alpha is not None:
        node["alpha"] = alpha
    if beta is not None:
        node["beta"] = beta
    return node


# ---------- Minimax ----------

def minimax(board, depth, maximizing_player, record_tree=False):
    """Standard Minimax algorithm.

    Returns (column, score) and optionally a tree dict.
    """
    tree = None

    valid_locations = get_valid_locations(board)
    terminal = is_terminal_node(board)

    if depth == 0 or terminal:
        if terminal:
            if check_win(board, AI_PIECE):
                score = 100_000_000
            elif check_win(board, PLAYER_PIECE):
                score = -100_000_000
            else:
                score = 0
        else:
            score = score_position(board, AI_PIECE)
        if record_tree:
            tree = _new_node(None, score, "leaf", depth)
        return (None, score, tree) if record_tree else (None, score)

    if maximizing_player:
        value = -math.inf
        best_col = random.choice(valid_locations)
        children = []
        for col in valid_locations:
            new_board = make_move(board, col, AI_PIECE)
            if record_tree:
                _, new_score, child_tree = minimax(
                    new_board, depth - 1, False, record_tree=True
                )
                child_node = _new_node(col, new_score, "max", depth - 1,
                                       children=child_tree.get("children", [])
                                       if child_tree else [])
                child_node["score"] = new_score
                children.append(child_node)
            else:
                _, new_score = minimax(new_board, depth - 1, False)
            if new_score > value:
                value = new_score
                best_col = col
        if record_tree:
            tree = _new_node(best_col, value, "max", depth, children=children)
        return (best_col, value, tree) if record_tree else (best_col, value)
    else:
        value = math.inf
        best_col = random.choice(valid_locations)
        children = []
        for col in valid_locations:
            new_board = make_move(board, col, PLAYER_PIECE)
            if record_tree:
                _, new_score, child_tree = minimax(
                    new_board, depth - 1, True, record_tree=True
                )
                child_node = _new_node(col, new_score, "min", depth - 1,
                                       children=child_tree.get("children", [])
                                       if child_tree else [])
                child_node["score"] = new_score
                children.append(child_node)
            else:
                _, new_score = minimax(new_board, depth - 1, True)
            if new_score < value:
                value = new_score
                best_col = col
        if record_tree:
            tree = _new_node(best_col, value, "min", depth, children=children)
        return (best_col, value, tree) if record_tree else (best_col, value)


# ---------- Alpha-Beta Pruning ----------

def alpha_beta(board, depth, alpha, beta, maximizing_player, record_tree=False):
    """Minimax with Alpha-Beta pruning.

    Returns (column, score) and optionally a tree dict.
    """
    tree = None

    valid_locations = get_valid_locations(board)
    terminal = is_terminal_node(board)

    if depth == 0 or terminal:
        if terminal:
            if check_win(board, AI_PIECE):
                score = 100_000_000
            elif check_win(board, PLAYER_PIECE):
                score = -100_000_000
            else:
                score = 0
        else:
            score = score_position(board, AI_PIECE)
        if record_tree:
            tree = _new_node(None, score, "leaf", depth, alpha=alpha, beta=beta)
        return (None, score, tree) if record_tree else (None, score)

    if maximizing_player:
        value = -math.inf
        best_col = random.choice(valid_locations)
        children = []
        for col in valid_locations:
            new_board = make_move(board, col, AI_PIECE)
            if record_tree:
                _, new_score, child_tree = alpha_beta(
                    new_board, depth - 1, alpha, beta, False, record_tree=True
                )
                child_node = _new_node(col, new_score, "max", depth - 1,
                                       alpha=alpha, beta=beta,
                                       children=child_tree.get("children", [])
                                       if child_tree else [])
                child_node["score"] = new_score
                pruned = False
            else:
                _, new_score = alpha_beta(
                    new_board, depth - 1, alpha, beta, False
                )
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if record_tree:
                child_node["alpha"] = alpha
                child_node["beta"] = beta
                children.append(child_node)
            if alpha >= beta:
                if record_tree:
                    # Mark remaining columns as pruned
                    remaining = [c for c in valid_locations
                                 if c not in [ch["col"] for ch in children]]
                    for rc in remaining:
                        children.append(_new_node(rc, None, "pruned", depth - 1,
                                                  alpha=alpha, beta=beta))
                break
        if record_tree:
            tree = _new_node(best_col, value, "max", depth,
                             alpha=alpha, beta=beta, children=children)
        return (best_col, value, tree) if record_tree else (best_col, value)
    else:
        value = math.inf
        best_col = random.choice(valid_locations)
        children = []
        for col in valid_locations:
            new_board = make_move(board, col, PLAYER_PIECE)
            if record_tree:
                _, new_score, child_tree = alpha_beta(
                    new_board, depth - 1, alpha, beta, True, record_tree=True
                )
                child_node = _new_node(col, new_score, "min", depth - 1,
                                       alpha=alpha, beta=beta,
                                       children=child_tree.get("children", [])
                                       if child_tree else [])
                child_node["score"] = new_score
            else:
                _, new_score = alpha_beta(
                    new_board, depth - 1, alpha, beta, True
                )
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if record_tree:
                child_node["alpha"] = alpha
                child_node["beta"] = beta
                children.append(child_node)
            if alpha >= beta:
                if record_tree:
                    remaining = [c for c in valid_locations
                                 if c not in [ch["col"] for ch in children]]
                    for rc in remaining:
                        children.append(_new_node(rc, None, "pruned", depth - 1,
                                                  alpha=alpha, beta=beta))
                break
        if record_tree:
            tree = _new_node(best_col, value, "min", depth,
                             alpha=alpha, beta=beta, children=children)
        return (best_col, value, tree) if record_tree else (best_col, value)


# ---------- Expectimax ----------

def expectimax(board, depth, maximizing_player, record_tree=False):
    """Expectimax algorithm (chance nodes replace min nodes).

    Returns (column, score) and optionally a tree dict.
    """
    tree = None

    valid_locations = get_valid_locations(board)
    terminal = is_terminal_node(board)

    if depth == 0 or terminal:
        if terminal:
            if check_win(board, AI_PIECE):
                score = 100_000_000
            elif check_win(board, PLAYER_PIECE):
                score = -100_000_000
            else:
                score = 0
        else:
            score = score_position(board, AI_PIECE)
        if record_tree:
            tree = _new_node(None, score, "leaf", depth)
        return (None, score, tree) if record_tree else (None, score)

    if maximizing_player:
        value = -math.inf
        best_col = random.choice(valid_locations)
        children = []
        for col in valid_locations:
            new_board = make_move(board, col, AI_PIECE)
            if record_tree:
                _, new_score, child_tree = expectimax(
                    new_board, depth - 1, False, record_tree=True
                )
                child_node = _new_node(col, new_score, "max", depth - 1,
                                       children=child_tree.get("children", [])
                                       if child_tree else [])
                child_node["score"] = new_score
                children.append(child_node)
            else:
                _, new_score = expectimax(new_board, depth - 1, False)
            if new_score > value:
                value = new_score
                best_col = col
        if record_tree:
            tree = _new_node(best_col, value, "max", depth, children=children)
        return (best_col, value, tree) if record_tree else (best_col, value)
    else:
        # Chance node: average over all opponent moves
        children = []
        total_score = 0
        n = len(valid_locations)
        for col in valid_locations:
            new_board = make_move(board, col, PLAYER_PIECE)
            if record_tree:
                _, new_score, child_tree = expectimax(
                    new_board, depth - 1, True, record_tree=True
                )
                child_node = _new_node(col, new_score, "chance", depth - 1,
                                       children=child_tree.get("children", [])
                                       if child_tree else [])
                child_node["score"] = new_score
                children.append(child_node)
            else:
                _, new_score = expectimax(new_board, depth - 1, True)
            total_score += new_score
        avg_score = total_score / n if n > 0 else 0
        # Expectimax chance node doesn't pick a "best" column;
        # the parent max node uses the averaged value.
        if record_tree:
            tree = _new_node(None, avg_score, "chance", depth,
                             children=children)
        return (None, avg_score, tree) if record_tree else (None, avg_score)
