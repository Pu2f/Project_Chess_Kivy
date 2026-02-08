from __future__ import annotations

from engine.types import Position, Move
from engine.rules import generate_legal_moves, apply_move, is_in_check


FILES = "abcdefgh"
RANKS = "12345678"


def sq_name(sq: int) -> str:
    f = sq % 8
    r = sq // 8
    return f"{FILES[f]}{RANKS[r]}"


def piece_letter(piece: str) -> str:
    # SAN uses uppercase piece letter for non-pawns; pawn is empty
    pl = piece.lower()
    if pl == "p":
        return ""
    return pl.upper()


def _is_capture(pos: Position, move: Move) -> bool:
    if move.is_en_passant:
        return True
    return pos.board[move.to_sq] != "."


def _promotion_suffix(move: Move) -> str:
    if move.promo is None:
        return ""
    if move.promo == "?":
        # should not happen in finalized move
        return ""
    return f"={move.promo.upper()}"


def _castle_san(pos: Position, move: Move) -> str | None:
    piece = pos.board[move.from_sq]
    if piece.lower() != "k" or not move.is_castle:
        return None
    # king destinations: g-file = O-O, c-file = O-O-O
    to_file = move.to_sq % 8
    if to_file == 6:
        return "O-O"
    if to_file == 2:
        return "O-O-O"
    return None


def _disambiguation(pos: Position, move: Move) -> str:
    """
    For pieces (not pawn/king castling): if two same-type pieces can move to same destination,
    add file or rank or both for origin.
    """
    piece = pos.board[move.from_sq]
    pl = piece.lower()
    if pl in ("p", "k"):
        return ""

    all_legal = generate_legal_moves(pos)
    same = []
    for m in all_legal:
        if m.to_sq != move.to_sq:
            continue
        if m.from_sq == move.from_sq:
            continue
        if pos.board[m.from_sq] == piece:
            same.append(m)

    if not same:
        return ""

    from_f = move.from_sq % 8
    from_r = move.from_sq // 8

    file_conflict = any((m.from_sq % 8) == from_f for m in same)
    rank_conflict = any((m.from_sq // 8) == from_r for m in same)

    # SAN rule: prefer file, if still ambiguous add rank, else both
    if not file_conflict:
        return FILES[from_f]
    if not rank_conflict:
        return RANKS[from_r]
    return f"{FILES[from_f]}{RANKS[from_r]}"


def move_to_san(pos: Position, move: Move) -> str:
    """
    Convert a *legal, fully specified* move to SAN.
    Assumes move.promo is concrete (q/r/b/n) for promotions.
    """
    # Castling
    castle = _castle_san(pos, move)
    if castle is not None:
        next_pos = apply_move(pos, move)
        suffix = _check_suffix(next_pos)
        return castle + suffix

    piece = pos.board[move.from_sq]
    pl = piece.lower()

    capture = _is_capture(pos, move)
    to_sq = move.to_sq
    to_name = sq_name(to_sq)

    if pl == "p":
        # pawn: capture includes from-file
        if capture:
            san = f"{FILES[move.from_sq % 8]}x{to_name}"
        else:
            san = f"{to_name}"
        san += _promotion_suffix(move)
    else:
        san = piece_letter(piece)
        san += _disambiguation(pos, move)
        if capture:
            san += "x"
        san += to_name
        # (No explicit "e.p." in strict SAN; commonly omitted. We omit.)
        # promotion is pawn-only

    next_pos = apply_move(pos, move)
    san += _check_suffix(next_pos)
    return san


def _check_suffix(next_pos: Position) -> str:
    """
    After a move is applied, check if side to move is in check/checkmate.
    """
    side_in_check = is_in_check(next_pos, next_pos.side_to_move)
    if not side_in_check:
        return ""

    # checkmate if no legal moves
    if len(generate_legal_moves(next_pos)) == 0:
        return "#"
    return "+"
