from chess_core.pieces import *
from chess_core.square import *
from chess_core.board import *
import copy


# =========================
# CHECK
# =========================


def check_for_check(board: Board, iswhite: bool) -> bool:

    king_square = None

    for line in board.board:
        for square in line:
            if isinstance(square.piece, King) and square.piece.iswhite == iswhite:
                king_square = square
                break

    if king_square is None:
        return False

    for line in board.board:
        for square in line:

            if isinstance(square.piece, EmptySquare):
                continue

            if square.piece.iswhite == iswhite:
                continue

            if isinstance(square.piece, Rook):
                if has_path_rook(board, square, king_square):
                    return True

            elif isinstance(square.piece, Bishop):
                if has_path_bishop(board, square, king_square):
                    return True

            elif isinstance(square.piece, Queen):
                if has_path_rook(board, square, king_square) or has_path_bishop(
                    board, square, king_square
                ):
                    return True

            elif isinstance(square.piece, Knight):
                if square.piece.possible_move(square, king_square):
                    return True

            elif isinstance(square.piece, King):
                if square.piece.possible_move(square, king_square):
                    return True

            elif isinstance(square.piece, Pawn):
                if pawn_can_capture(board, square, king_square):
                    return True

    return False


# =========================
# END TURN
# =========================


def end_turn(board: Board, iswhite: bool):

    for line in board.board:
        for square in line:
            if isinstance(square.piece, Pawn):
                if square.piece.iswhite != iswhite:
                    square.piece.en_passantable = False

    line_index = 7 if iswhite else 0

    for y in range(8):
        square = board.board[line_index][y]

        if isinstance(square.piece, Pawn) and square.piece.iswhite == iswhite:
            return square

    return None


# =========================
# TURN
# =========================


def turn(board: Board, x1, y1, x2, y2, iswhite, check=False):

    if not (0 <= x1 < 8 and 0 <= y1 < 8 and 0 <= x2 < 8 and 0 <= y2 < 8):
        return False

    start = board.board[x1][y1]
    end = board.board[x2][y2]

    if start.piece.iswhite != iswhite:
        return False

    board_copy = copy.deepcopy(board)

    start_copy = board_copy.board[x1][y1]
    end_copy = board_copy.board[x2][y2]

    if not move_piece(board_copy, start_copy, end_copy):
        return False

    if check_for_check(board_copy, iswhite):
        return False

    if check:
        return True

    # apply move จริง
    move_piece(board, start, end)

    promotion_square = end_turn(board, iswhite)

    if promotion_square is not None:
        return promotion_square

    return True
