from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from engine.types import Position, Move


# Direction helpers (rank/file)
KNIGHT_DELTAS = [
    (+2, +1),
    (+2, -1),
    (-2, +1),
    (-2, -1),
    (+1, +2),
    (+1, -2),
    (-1, +2),
    (-1, -2),
]
KING_DELTAS = [
    (dr, df) for dr in (-1, 0, 1) for df in (-1, 0, 1) if not (dr == 0 and df == 0)
]

BISHOP_DIRS = [(+1, +1), (+1, -1), (-1, +1), (-1, -1)]
ROOK_DIRS = [(+1, 0), (-1, 0), (0, +1), (0, -1)]
QUEEN_DIRS = BISHOP_DIRS + ROOK_DIRS


def rf(sq: int) -> tuple[int, int]:
    return sq // 8, sq % 8


def on_board(r: int, f: int) -> bool:
    return 0 <= r < 8 and 0 <= f < 8


def sq_of(r: int, f: int) -> int:
    return r * 8 + f


def is_white(p: str) -> bool:
    return p != "." and p.isupper()


def is_black(p: str) -> bool:
    return p != "." and p.islower()


def same_side(piece: str, side: str) -> bool:
    return (side == "w" and is_white(piece)) or (side == "b" and is_black(piece))


def enemy_side(piece: str, side: str) -> bool:
    return (side == "w" and is_black(piece)) or (side == "b" and is_white(piece))


def find_king(pos: Position, side: str) -> int:
    target = "K" if side == "w" else "k"
    for i, p in enumerate(pos.board):
        if p == target:
            return i
    raise ValueError("King not found in position")


def attacked_by_side(pos: Position, attacker_side: str) -> set[int]:
    """
    Squares attacked by attacker_side (w/b).
    Used for check detection and (later) castling legality.
    """
    attacks: set[int] = set()
    b = pos.board

    for from_sq, p in enumerate(b):
        if p == "." or not same_side(p, attacker_side):
            continue

        pr, pf = rf(from_sq)
        pl = p.lower()

        if pl == "p":
            # Pawn attacks only (not moves)
            dr = +1 if attacker_side == "w" else -1
            for df in (-1, +1):
                tr, tf = pr + dr, pf + df
                if on_board(tr, tf):
                    attacks.add(sq_of(tr, tf))

        elif pl == "n":
            for dr, df in KNIGHT_DELTAS:
                tr, tf = pr + dr, pf + df
                if on_board(tr, tf):
                    attacks.add(sq_of(tr, tf))

        elif pl == "k":
            for dr, df in KING_DELTAS:
                tr, tf = pr + dr, pf + df
                if on_board(tr, tf):
                    attacks.add(sq_of(tr, tf))

        elif pl in ("b", "r", "q"):
            dirs = BISHOP_DIRS if pl == "b" else ROOK_DIRS if pl == "r" else QUEEN_DIRS
            for dr, df in dirs:
                tr, tf = pr + dr, pf + df
                while on_board(tr, tf):
                    to_sq = sq_of(tr, tf)
                    attacks.add(to_sq)
                    if b[to_sq] != ".":
                        break
                    tr += dr
                    tf += df

    return attacks


def is_in_check(pos: Position, side: str) -> bool:
    king_sq = find_king(pos, side)
    opp = "b" if side == "w" else "w"
    return king_sq in attacked_by_side(pos, opp)


def apply_move_basic(pos: Position, move: Move) -> Position:
    """
    Apply move without special moves (no castling, en passant, promotion) — Part 1.
    Keeps castling/en-passant fields as-is for now; later parts will handle them properly.
    """
    b = pos.board[:]
    piece = b[move.from_sq]
    b[move.from_sq] = "."
    b[move.to_sq] = piece

    next_side = "b" if pos.side_to_move == "w" else "w"
    # halfmove clock: reset on capture or pawn move (pawn move detection by lower() == 'p')
    is_capture = pos.board[move.to_sq] != "."
    is_pawn = piece.lower() == "p"
    halfmove = 0 if (is_capture or is_pawn) else (pos.halfmove_clock + 1)
    fullmove = pos.fullmove_number + (1 if next_side == "w" else 0)

    return Position(
        board=b,
        side_to_move=next_side,
        castling=pos.castling,
        en_passant_sq=None,  # later: set when double pawn push
        halfmove_clock=halfmove,
        fullmove_number=fullmove,
    )


def generate_pseudo_legal_moves(pos: Position) -> list[Move]:
    side = pos.side_to_move
    b = pos.board
    moves: list[Move] = []

    for from_sq, p in enumerate(b):
        if p == "." or not same_side(p, side):
            continue

        fr, ff = rf(from_sq)
        pl = p.lower()

        if pl == "p":
            dr = +1 if side == "w" else -1
            start_rank = 1 if side == "w" else 6

            # single push
            tr = fr + dr
            if on_board(tr, ff):
                to_sq = sq_of(tr, ff)
                if b[to_sq] == ".":
                    moves.append(Move(from_sq, to_sq))

                    # double push
                    if fr == start_rank:
                        tr2 = fr + 2 * dr
                        to_sq2 = sq_of(tr2, ff)
                        if on_board(tr2, ff) and b[to_sq2] == ".":
                            moves.append(Move(from_sq, to_sq2))

            # captures
            for df in (-1, +1):
                tr, tf = fr + dr, ff + df
                if not on_board(tr, tf):
                    continue
                to_sq = sq_of(tr, tf)
                if enemy_side(b[to_sq], side):
                    moves.append(Move(from_sq, to_sq))

            # en passant later

        elif pl == "n":
            for dr, df in KNIGHT_DELTAS:
                tr, tf = fr + dr, ff + df
                if not on_board(tr, tf):
                    continue
                to_sq = sq_of(tr, tf)
                if not same_side(b[to_sq], side):
                    moves.append(Move(from_sq, to_sq))

        elif pl == "k":
            for dr, df in KING_DELTAS:
                tr, tf = fr + dr, ff + df
                if not on_board(tr, tf):
                    continue
                to_sq = sq_of(tr, tf)
                if not same_side(b[to_sq], side):
                    moves.append(Move(from_sq, to_sq))
            # castling later

        elif pl in ("b", "r", "q"):
            dirs = BISHOP_DIRS if pl == "b" else ROOK_DIRS if pl == "r" else QUEEN_DIRS
            for dr, df in dirs:
                tr, tf = fr + dr, ff + df
                while on_board(tr, tf):
                    to_sq = sq_of(tr, tf)
                    if same_side(b[to_sq], side):
                        break
                    moves.append(Move(from_sq, to_sq))
                    if enemy_side(b[to_sq], side):
                        break
                    tr += dr
                    tf += df

    return moves


def generate_legal_moves(pos: Position) -> list[Move]:
    """
    Legal = pseudo-legal filtered by 'cannot leave your king in check'.
    Special moves will be added in later parts.
    """
    legal: list[Move] = []
    for m in generate_pseudo_legal_moves(pos):
        new_pos = apply_move_basic(pos, m)
        if not is_in_check(new_pos, "b" if new_pos.side_to_move == "w" else "w"):
            legal.append(m)
    return legal
