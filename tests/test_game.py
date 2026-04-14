"""Tests for the core Connect-4 game logic."""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import (
    AI_PIECE,
    COLS,
    EMPTY,
    PLAYER_PIECE,
    ROWS,
    check_win,
    create_board,
    get_next_open_row,
    get_valid_locations,
    is_draw,
    is_terminal_node,
    is_valid_location,
    make_move,
    score_position,
)


class TestCreateBoard(unittest.TestCase):
    def test_dimensions(self):
        board = create_board()
        self.assertEqual(len(board), ROWS)
        for row in board:
            self.assertEqual(len(row), COLS)

    def test_all_empty(self):
        board = create_board()
        for row in board:
            for cell in row:
                self.assertEqual(cell, EMPTY)


class TestValidLocation(unittest.TestCase):
    def test_empty_board(self):
        board = create_board()
        for c in range(COLS):
            self.assertTrue(is_valid_location(board, c))

    def test_full_column(self):
        board = create_board()
        for r in range(ROWS):
            board[r][0] = PLAYER_PIECE
        self.assertFalse(is_valid_location(board, 0))

    def test_out_of_range(self):
        board = create_board()
        self.assertFalse(is_valid_location(board, -1))
        self.assertFalse(is_valid_location(board, COLS))

    def test_get_valid_locations(self):
        board = create_board()
        self.assertEqual(get_valid_locations(board), list(range(COLS)))


class TestGetNextOpenRow(unittest.TestCase):
    def test_empty_column(self):
        board = create_board()
        self.assertEqual(get_next_open_row(board, 0), ROWS - 1)

    def test_partially_filled(self):
        board = create_board()
        board[ROWS - 1][3] = PLAYER_PIECE
        self.assertEqual(get_next_open_row(board, 3), ROWS - 2)

    def test_full_column(self):
        board = create_board()
        for r in range(ROWS):
            board[r][2] = AI_PIECE
        self.assertEqual(get_next_open_row(board, 2), -1)


class TestMakeMove(unittest.TestCase):
    def test_returns_new_board(self):
        board = create_board()
        new_board = make_move(board, 3, PLAYER_PIECE)
        self.assertIsNotNone(new_board)
        self.assertIsNot(board, new_board)
        self.assertEqual(new_board[ROWS - 1][3], PLAYER_PIECE)
        # Original unchanged
        self.assertEqual(board[ROWS - 1][3], EMPTY)

    def test_invalid_move_returns_none(self):
        board = create_board()
        for r in range(ROWS):
            board[r][0] = AI_PIECE
        self.assertIsNone(make_move(board, 0, PLAYER_PIECE))


class TestCheckWin(unittest.TestCase):
    def test_horizontal_win(self):
        board = create_board()
        for c in range(4):
            board[ROWS - 1][c] = PLAYER_PIECE
        self.assertTrue(check_win(board, PLAYER_PIECE))
        self.assertFalse(check_win(board, AI_PIECE))

    def test_vertical_win(self):
        board = create_board()
        for r in range(ROWS - 4, ROWS):
            board[r][0] = AI_PIECE
        self.assertTrue(check_win(board, AI_PIECE))

    def test_positive_diagonal_win(self):
        board = create_board()
        for i in range(4):
            board[ROWS - 1 - i][i] = PLAYER_PIECE
        self.assertTrue(check_win(board, PLAYER_PIECE))

    def test_negative_diagonal_win(self):
        board = create_board()
        for i in range(4):
            board[i][i] = AI_PIECE
        self.assertTrue(check_win(board, AI_PIECE))

    def test_no_win(self):
        board = create_board()
        board[ROWS - 1][0] = PLAYER_PIECE
        board[ROWS - 1][1] = PLAYER_PIECE
        self.assertFalse(check_win(board, PLAYER_PIECE))


class TestTerminalAndDraw(unittest.TestCase):
    def test_empty_board_not_terminal(self):
        board = create_board()
        self.assertFalse(is_terminal_node(board))
        self.assertFalse(is_draw(board))

    def test_win_is_terminal(self):
        board = create_board()
        for c in range(4):
            board[ROWS - 1][c] = PLAYER_PIECE
        self.assertTrue(is_terminal_node(board))
        self.assertFalse(is_draw(board))

    def test_full_board_draw(self):
        # Fill board with alternating pieces, no four in a row
        board = create_board()
        pattern = [
            [1, 2, 1, 2, 1, 2, 1],
            [1, 2, 1, 2, 1, 2, 1],
            [2, 1, 2, 1, 2, 1, 2],
            [1, 2, 1, 2, 1, 2, 1],
            [1, 2, 1, 2, 1, 2, 1],
            [2, 1, 2, 1, 2, 1, 2],
        ]
        for r in range(ROWS):
            for c in range(COLS):
                board[r][c] = pattern[r][c]
        # Verify no winner
        self.assertFalse(check_win(board, PLAYER_PIECE))
        self.assertFalse(check_win(board, AI_PIECE))
        self.assertTrue(is_terminal_node(board))
        self.assertTrue(is_draw(board))


class TestScorePosition(unittest.TestCase):
    def test_empty_board_score(self):
        board = create_board()
        score = score_position(board, AI_PIECE)
        self.assertEqual(score, 0)

    def test_centre_preference(self):
        board = create_board()
        board[ROWS - 1][COLS // 2] = AI_PIECE
        score = score_position(board, AI_PIECE)
        self.assertGreater(score, 0)


if __name__ == "__main__":
    unittest.main()
