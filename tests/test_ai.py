"""Tests for the adversarial AI algorithms."""

import math
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai import alpha_beta, expectimax, minimax
from game import (
    AI_PIECE,
    COLS,
    PLAYER_PIECE,
    ROWS,
    check_win,
    create_board,
    get_valid_locations,
    make_move,
)


class TestMinimax(unittest.TestCase):
    def test_returns_valid_column(self):
        board = create_board()
        col, score = minimax(board, 3, True)
        self.assertIn(col, get_valid_locations(board))

    def test_blocks_opponent_win(self):
        """AI should block an imminent horizontal win by the player."""
        board = create_board()
        # Player has 3 in a row at bottom, cols 0-2
        for c in range(3):
            board[ROWS - 1][c] = PLAYER_PIECE
        col, score = minimax(board, 4, True)
        # AI should play col 3 to block
        self.assertEqual(col, 3)

    def test_takes_winning_move(self):
        """AI should take an immediate winning move."""
        board = create_board()
        for c in range(3):
            board[ROWS - 1][c] = AI_PIECE
        col, score = minimax(board, 4, True)
        self.assertEqual(col, 3)

    def test_tree_recording(self):
        board = create_board()
        col, score, tree = minimax(board, 2, True, record_tree=True)
        self.assertIsNotNone(tree)
        self.assertIn("children", tree)
        self.assertIn("score", tree)
        self.assertIn("type", tree)
        self.assertGreater(len(tree["children"]), 0)


class TestAlphaBeta(unittest.TestCase):
    def test_returns_valid_column(self):
        board = create_board()
        col, score = alpha_beta(board, 3, -math.inf, math.inf, True)
        self.assertIn(col, get_valid_locations(board))

    def test_same_result_as_minimax(self):
        """Alpha-beta should return the same score as minimax."""
        board = create_board()
        board[ROWS - 1][3] = PLAYER_PIECE
        board[ROWS - 1][4] = AI_PIECE

        _, mm_score = minimax(board, 3, True)
        _, ab_score = alpha_beta(board, 3, -math.inf, math.inf, True)
        self.assertEqual(mm_score, ab_score)

    def test_blocks_opponent_win(self):
        board = create_board()
        for c in range(3):
            board[ROWS - 1][c] = PLAYER_PIECE
        col, _ = alpha_beta(board, 4, -math.inf, math.inf, True)
        self.assertEqual(col, 3)

    def test_tree_has_pruned_nodes(self):
        board = create_board()
        board[ROWS - 1][3] = PLAYER_PIECE
        _, _, tree = alpha_beta(board, 3, -math.inf, math.inf, True,
                                record_tree=True)
        self.assertIsNotNone(tree)
        # Tree should have alpha/beta values
        self.assertIn("alpha", tree)
        self.assertIn("beta", tree)


class TestExpectimax(unittest.TestCase):
    def test_returns_valid_column(self):
        board = create_board()
        col, score = expectimax(board, 3, True)
        self.assertIn(col, get_valid_locations(board))

    def test_takes_winning_move(self):
        board = create_board()
        for c in range(3):
            board[ROWS - 1][c] = AI_PIECE
        col, score = expectimax(board, 4, True)
        self.assertEqual(col, 3)

    def test_tree_has_chance_nodes(self):
        board = create_board()
        _, _, tree = expectimax(board, 2, True, record_tree=True)
        self.assertIsNotNone(tree)

        # Find a chance node in the tree
        def has_chance(node):
            if node.get("type") == "chance":
                return True
            return any(has_chance(c) for c in node.get("children", []))

        self.assertTrue(has_chance(tree))


if __name__ == "__main__":
    unittest.main()
