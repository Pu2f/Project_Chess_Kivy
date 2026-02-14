from __future__ import annotations

from chess_core.board import Board
from chess_core.square import EmptySquare
from chess_core.pieces import King, Queen, Rook, Bishop, Knight, Pawn

_FILES = "abcdefgh"


def _piece_to_fen_char(piece) -> str:
    if isinstance(piece, EmptySquare):
        raise ValueError("EmptySquare cannot be converted to FEN piece char")

    if isinstance(piece, King):
        ch = "k"
    elif isinstance(piece, Queen):
        ch = "q"
    elif isinstance(piece, Rook):
        ch = "r"
    elif isinstance(piece, Bishop):
        ch = "b"
    elif isinstance(piece, Knight):
        ch = "n"
    elif isinstance(piece, Pawn):
        ch = "p"
    else:
        raise TypeError(f"Unknown piece type: {type(piece)}")

    return ch.upper() if piece.iswhite else ch


def _board_placement() -> str:
    """
    Board.board[x][y]
      x=0 -> rank1
      x=7 -> rank8
    แต่ FEN ต้องเรียง rank8 -> rank1
    """
    ranks = []
    for x in range(7, -1, -1):
        empty = 0
        row = []
        for y in range(8):
            piece = Board.board[x][y].piece
            if isinstance(piece, EmptySquare):
                empty += 1
            else:
                if empty:
                    row.append(str(empty))
                    empty = 0
                row.append(_piece_to_fen_char(piece))
        if empty:
            row.append(str(empty))
        ranks.append("".join(row))
    return "/".join(ranks)


def _castling_rights() -> str:
    """
    คำนวณสิทธิ์เข้าปราสาทจากตำแหน่งมาตรฐาน + flag moved
    - White king e1: (0,4), rooks a1/h1: (0,0)/(0,7)
    - Black king e8: (7,4), rooks a8/h8: (7,0)/(7,7)
    """
    rights = []

    # White
    wk = Board.board[0][4].piece
    if isinstance(wk, King) and wk.iswhite and (not wk.moved):
        wr_h = Board.board[0][7].piece
        wr_a = Board.board[0][0].piece
        if isinstance(wr_h, Rook) and wr_h.iswhite and (not wr_h.moved):
            rights.append("K")
        if isinstance(wr_a, Rook) and wr_a.iswhite and (not wr_a.moved):
            rights.append("Q")

    # Black
    bk = Board.board[7][4].piece
    if isinstance(bk, King) and (not bk.iswhite) and (not bk.moved):
        br_h = Board.board[7][7].piece
        br_a = Board.board[7][0].piece
        if isinstance(br_h, Rook) and (not br_h.iswhite) and (not br_h.moved):
            rights.append("k")
        if isinstance(br_a, Rook) and (not br_a.iswhite) and (not br_a.moved):
            rights.append("q")

    return "".join(rights) if rights else "-"


def _en_passant_target() -> str:
    """
    คืนค่า ep-target square สำหรับ FEN เช่น e3/e6 หรือ '-'

    model ของคุณ:
    - Pawn.en_passantable=True เมื่อเดิน 2 ช่อง
    - white: x 1->3 (pawn อยู่ x=3) => target x=2 => rank3 => rank = x
    - black: x 6->4 (pawn อยู่ x=4) => target x=5 => rank6 => rank = x+2
    """
    for x in range(8):
        for y in range(8):
            p = Board.board[x][y].piece
            if isinstance(p, Pawn) and getattr(p, "en_passantable", False):
                file_ = _FILES[y]
                if p.iswhite:
                    return f"{file_}{x}"
                return f"{file_}{x + 2}"
    return "-"


def to_fen(
    side_to_move_iswhite: bool,
    halfmove_clock: int = 0,
    fullmove_number: int = 1,
) -> str:
    placement = _board_placement()
    active = "w" if side_to_move_iswhite else "b"
    castling = _castling_rights()
    ep = _en_passant_target()
    return f"{placement} {active} {castling} {ep} {halfmove_clock} {fullmove_number}"