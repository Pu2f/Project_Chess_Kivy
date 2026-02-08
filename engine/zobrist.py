from __future__ import annotations

import random
from dataclasses import dataclass

from engine.types import Position


PIECES = ["P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k"]
PIECE_INDEX = {p: i for i, p in enumerate(PIECES)}


@dataclass(frozen=True)
class ZobristKeys:
    piece_square: list[list[int]]  # [12][64]
    side_to_move: int
    castling: list[int]  # 16 possibilities
    en_passant_file: list[int]  # 9 (0..7 file, 8 = none)


def make_keys(seed: int = 20260205) -> ZobristKeys:
    rng = random.Random(seed)
    piece_square = [[rng.getrandbits(64) for _ in range(64)] for _ in range(12)]
    side_to_move = rng.getrandbits(64)
    castling = [rng.getrandbits(64) for _ in range(16)]
    en_passant_file = [rng.getrandbits(64) for _ in range(9)]
    return ZobristKeys(piece_square, side_to_move, castling, en_passant_file)


_KEYS = make_keys()


def _castling_mask(pos: Position) -> int:
    m = 0
    if pos.castling.wk:
        m |= 1
    if pos.castling.wq:
        m |= 2
    if pos.castling.bk:
        m |= 4
    if pos.castling.bq:
        m |= 8
    return m


def hash_position(pos: Position) -> int:
    """
    Hash for repetition: includes pieces, side, castling, en passant file.
    (Does NOT include halfmove/fullmove per repetition rules)
    """
    h = 0
    for sq, p in enumerate(pos.board):
        if p == ".":
            continue
        h ^= _KEYS.piece_square[PIECE_INDEX[p]][sq]

    if pos.side_to_move == "w":
        h ^= _KEYS.side_to_move

    h ^= _KEYS.castling[_castling_mask(pos)]

    if pos.en_passant_sq is None:
        h ^= _KEYS.en_passant_file[8]
    else:
        f = pos.en_passant_sq % 8
        h ^= _KEYS.en_passant_file[f]

    return h
