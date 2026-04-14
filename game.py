"""Core Connect-4 game logic."""

import copy

ROWS = 6
COLS = 7
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
WINDOW_LENGTH = 4


def create_board():
    """Create an empty Connect-4 board."""
    return [[EMPTY] * COLS for _ in range(ROWS)]


def is_valid_location(board, col):
    """Check if a column has space for another piece."""
    return 0 <= col < COLS and board[0][col] == EMPTY


def get_valid_locations(board):
    """Return list of columns that are not full."""
    return [col for col in range(COLS) if is_valid_location(board, col)]


def get_next_open_row(board, col):
    """Return the lowest empty row in the given column, or -1 if full."""
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            return row
    return -1


def drop_piece(board, row, col, piece):
    """Place a piece on the board (mutates in place)."""
    board[row][col] = piece


def make_move(board, col, piece):
    """Return a new board with the piece dropped in the given column.

    Returns None if the column is full.
    """
    if not is_valid_location(board, col):
        return None
    new_board = copy.deepcopy(board)
    row = get_next_open_row(new_board, col)
    drop_piece(new_board, row, col, piece)
    return new_board


def check_win(board, piece):
    """Return True if the given piece has four in a row."""
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return True
    # Vertical
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(board[r + i][c] == piece for i in range(4)):
                return True
    # Positive diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True
    # Negative diagonal
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True
    return False


def is_terminal_node(board):
    """Check if the game is over (win or draw)."""
    return (check_win(board, PLAYER_PIECE)
            or check_win(board, AI_PIECE)
            or len(get_valid_locations(board)) == 0)


def is_draw(board):
    """Check if the game is a draw (board full, no winner)."""
    return (not check_win(board, PLAYER_PIECE)
            and not check_win(board, AI_PIECE)
            and len(get_valid_locations(board)) == 0)


def evaluate_window(window, piece):
    """Score a window of 4 cells."""
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    score = 0
    piece_count = window.count(piece)
    empty_count = window.count(EMPTY)
    opp_count = window.count(opp_piece)

    if piece_count == 4:
        score += 100
    elif piece_count == 3 and empty_count == 1:
        score += 5
    elif piece_count == 2 and empty_count == 2:
        score += 2

    if opp_count == 3 and empty_count == 1:
        score -= 4

    return score


def score_position(board, piece):
    """Evaluate the entire board for a given piece."""
    score = 0

    # Centre column preference
    centre_col = COLS // 2
    centre_array = [board[r][centre_col] for r in range(ROWS)]
    score += centre_array.count(piece) * 3

    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            window = [board[r][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Vertical
    for r in range(ROWS - 3):
        for c in range(COLS):
            window = [board[r + i][c] for i in range(4)]
            score += evaluate_window(window, piece)

    # Positive diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Negative diagonal
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score
