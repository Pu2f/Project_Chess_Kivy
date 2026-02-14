from chess_core.square import *
from chess_core.pieces import *


def board_range(num):
    if num == 0:
        return []
    if num >= 1:
        return range(1, num)
    if num <= -1:
        return range(-1, num, -1)


class Board:

    def __init__(self):
        self.board = []
        self.create_board()

    def create_board(self):

        self.board = []

        line = [
            Square(0, 0, Rook(True)),
            Square(0, 1, Knight(True)),
            Square(0, 2, Bishop(True)),
            Square(0, 3, Queen(True)),
            Square(0, 4, King(True)),
            Square(0, 5, Bishop(True)),
            Square(0, 6, Knight(True)),
            Square(0, 7, Rook(True)),
        ]
        self.board.append(line)

        self.board.append([Square(1, i, Pawn(True)) for i in range(8)])

        for i in range(2, 6):
            self.board.append([Square(i, j) for j in range(8)])

        self.board.append([Square(6, i, Pawn(False)) for i in range(8)])

        line = [
            Square(7, 0, Rook(False)),
            Square(7, 1, Knight(False)),
            Square(7, 2, Bishop(False)),
            Square(7, 3, Queen(False)),
            Square(7, 4, King(False)),
            Square(7, 5, Bishop(False)),
            Square(7, 6, Knight(False)),
            Square(7, 7, Rook(False)),
        ]
        self.board.append(line)

    def print_board(self):
        for row in self.board[::-1]:
            for sq in row:
                print(sq, end=" ")
            print()


# =========================
# Movement Functions
# =========================


def has_path_rook(board: Board, start: Square, end: Square):

    if not start.piece.possible_move(start, end):
        return False

    x = end.x - start.x
    y = end.y - start.y

    if x != 0:
        for i in board_range(x):
            if not isinstance(board.board[start.x + i][start.y].piece, EmptySquare):
                return False
        return True

    for i in board_range(y):
        if not isinstance(board.board[start.x][start.y + i].piece, EmptySquare):
            return False

    return True


def has_path_bishop(board: Board, start: Square, end: Square):

    if not start.piece.possible_move(start, end):
        return False

    x = end.x - start.x
    y = end.y - start.y

    if x == 0 or y == 0:
        return False

    for i, j in zip(board_range(x), board_range(y)):
        if not isinstance(board.board[start.x + i][start.y + j].piece, EmptySquare):
            return False

    return True


def pawn_can_capture(board: Board, start: Square, end: Square):

    x = end.x - start.x
    y = abs(end.y - start.y)

    if (
        not isinstance(end.piece, EmptySquare)
        and start.piece.iswhite != end.piece.iswhite
    ):
        if start.piece.iswhite and x == 1 and y == 1:
            return True
        if not start.piece.iswhite and x == -1 and y == 1:
            return True

    # en passant
    if isinstance(end.piece, EmptySquare) and isinstance(
        board.board[start.x][end.y].piece, Pawn
    ):
        target_pawn = board.board[start.x][end.y].piece
        if target_pawn.en_passantable:
            if start.piece.iswhite and x == 1 and y == 1:
                return True
            if not start.piece.iswhite and x == -1 and y == 1:
                return True

    return False


def can_castle(board: Board, start: Square, end: Square):

    x = end.x - start.x
    y = end.y - start.y

    if start.piece.moved or abs(y) != 2 or x != 0:
        return False

    if y > 0:
        rook_square = board.board[start.x][7]
        move_square = board.board[start.x][start.y + 1]
    else:
        rook_square = board.board[start.x][0]
        move_square = board.board[start.x][start.y - 1]

    if not isinstance(rook_square.piece, Rook) or rook_square.piece.moved:
        return False

    if has_path_rook(board, rook_square, move_square):
        move_piece(board, rook_square, move_square)
        return True

    return False


def move_piece(board: Board, start: Square, end: Square):

    piece = start.piece

    # ---------------- ROOK ----------------
    if isinstance(piece, Rook):
        if not has_path_rook(board, start, end):
            return False
        piece.moved = True

    # ---------------- BISHOP ----------------
    elif isinstance(piece, Bishop):
        if not has_path_bishop(board, start, end):
            return False

    # ---------------- QUEEN ----------------
    elif isinstance(piece, Queen):
        if not (has_path_rook(board, start, end) or has_path_bishop(board, start, end)):
            return False

    # ---------------- KING ----------------
    elif isinstance(piece, King):
        if not (piece.possible_move(start, end) or can_castle(board, start, end)):
            return False
        piece.moved = True

    # ---------------- KNIGHT ----------------
    elif isinstance(piece, Knight):
        if not piece.possible_move(start, end):
            return False

    # ---------------- PAWN ----------------
    elif isinstance(piece, Pawn):

        if not (
            (piece.possible_move(start, end) and isinstance(end.piece, EmptySquare))
            or pawn_can_capture(board, start, end)
        ):
            return False

        piece.moved = True

        # เดิน 2 ช่อง
        if abs(start.x - end.x) == 2:
            piece.en_passantable = True

        # en passant capture
        if isinstance(end.piece, EmptySquare) and start.y != end.y:
            board.board[start.x][end.y].piece = EmptySquare()

    else:
        return False

    # ---------------- MOVE ----------------
    board.board[end.x][end.y].piece = piece
    board.board[start.x][start.y].piece = EmptySquare()

    return True
