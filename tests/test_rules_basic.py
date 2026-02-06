import pytest

from engine.fen import parse_fen
from engine.rules import generate_legal_moves, is_in_check


def moves_from_to(moves, fr, to):
    return any(m.from_sq == fr and m.to_sq == to for m in moves)


def sq(name: str) -> int:
    # "a1" -> 0
    file = ord(name[0]) - ord("a")
    rank = int(name[1]) - 1
    return rank * 8 + file


def test_start_position_has_20_legal_moves_for_white():
    pos = parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    moves = generate_legal_moves(pos)
    assert len(moves) == 20


def test_pawn_double_push_blocked_not_allowed():
    # white pawn at e2 blocked by piece at e3
    pos = parse_fen("8/8/8/8/8/4p3/4P3/4K3 w - - 0 1")
    moves = generate_legal_moves(pos)
    assert not moves_from_to(moves, sq("e2"), sq("e3"))
    assert not moves_from_to(moves, sq("e2"), sq("e4"))


def test_knight_jumps():
    pos = parse_fen("8/8/8/8/8/8/4N3/4K3 w - - 0 1")
    moves = generate_legal_moves(pos)
    assert moves_from_to(moves, sq("e2"), sq("c1"))
    assert moves_from_to(moves, sq("e2"), sq("c3"))
    assert moves_from_to(moves, sq("e2"), sq("d4"))
    assert moves_from_to(moves, sq("e2"), sq("f4"))
    assert moves_from_to(moves, sq("e2"), sq("g3"))
    assert moves_from_to(moves, sq("e2"), sq("g1"))


def test_cannot_leave_king_in_check():
    # White king e1, white rook e2 pinned by black rook e8:
    # rook e2 cannot move away because it exposes check on king.
    pos = parse_fen("4r3/8/8/8/8/8/4R3/4K3 w - - 0 1")
    moves = generate_legal_moves(pos)
    # rook e2 -> e3 would expose king on e1 to rook e8
    assert not moves_from_to(moves, sq("e2"), sq("e3"))


def test_check_detection():
    pos = parse_fen("4r3/8/8/8/8/8/8/4K3 w - - 0 1")
    assert is_in_check(pos, "w") is True
