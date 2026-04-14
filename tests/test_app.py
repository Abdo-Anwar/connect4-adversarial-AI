"""Tests for the Flask web application."""

import json
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from game import AI_PIECE, COLS, PLAYER_PIECE, ROWS, create_board


class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.testing = True

    def test_index_page(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Connect 4", resp.data)

    def test_api_check_valid_move(self):
        board = create_board()
        resp = self.client.post(
            "/api/check",
            data=json.dumps({"board": board, "col": 3}),
            content_type="application/json",
        )
        data = resp.get_json()
        self.assertEqual(resp.status_code, 200)
        self.assertIn("board", data)
        self.assertEqual(data["board"][ROWS - 1][3], PLAYER_PIECE)
        self.assertIsNone(data["winner"])

    def test_api_check_invalid_move(self):
        board = create_board()
        for r in range(ROWS):
            board[r][0] = PLAYER_PIECE
        resp = self.client.post(
            "/api/check",
            data=json.dumps({"board": board, "col": 0}),
            content_type="application/json",
        )
        data = resp.get_json()
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", data)

    def test_api_move_minimax(self):
        board = create_board()
        resp = self.client.post(
            "/api/move",
            data=json.dumps({"board": board, "algorithm": "minimax", "depth": 2}),
            content_type="application/json",
        )
        data = resp.get_json()
        self.assertEqual(resp.status_code, 200)
        self.assertIn("col", data)
        self.assertIn("board", data)
        self.assertIn("tree", data)
        self.assertIn(data["col"], list(range(COLS)))

    def test_api_move_alphabeta(self):
        board = create_board()
        resp = self.client.post(
            "/api/move",
            data=json.dumps({"board": board, "algorithm": "alphabeta", "depth": 2}),
            content_type="application/json",
        )
        data = resp.get_json()
        self.assertEqual(resp.status_code, 200)
        self.assertIn("tree", data)
        # Alpha-beta tree should have alpha/beta
        tree = data["tree"]
        self.assertIn("alpha", tree)

    def test_api_move_expectimax(self):
        board = create_board()
        resp = self.client.post(
            "/api/move",
            data=json.dumps({"board": board, "algorithm": "expectimax", "depth": 2}),
            content_type="application/json",
        )
        data = resp.get_json()
        self.assertEqual(resp.status_code, 200)

    def test_api_move_unknown_algorithm(self):
        board = create_board()
        resp = self.client.post(
            "/api/move",
            data=json.dumps({"board": board, "algorithm": "unknown", "depth": 2}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_api_move_detects_ai_win(self):
        board = create_board()
        # Set up AI about to win (3 in a row)
        for c in range(3):
            board[ROWS - 1][c] = AI_PIECE
        resp = self.client.post(
            "/api/move",
            data=json.dumps({"board": board, "algorithm": "minimax", "depth": 2}),
            content_type="application/json",
        )
        data = resp.get_json()
        self.assertEqual(data["winner"], "ai")

    def test_api_check_detects_player_win(self):
        board = create_board()
        for c in range(3):
            board[ROWS - 1][c] = PLAYER_PIECE
        resp = self.client.post(
            "/api/check",
            data=json.dumps({"board": board, "col": 3}),
            content_type="application/json",
        )
        data = resp.get_json()
        self.assertEqual(data["winner"], "player")

    def test_api_move_missing_board(self):
        resp = self.client.post(
            "/api/move",
            data=json.dumps({"algorithm": "minimax"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
