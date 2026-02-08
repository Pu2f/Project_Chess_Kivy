from engine.fen import parse_fen
from engine.rules import generate_legal_moves
from engine.san import move_to_san


def sq(name: str) -> int:
    file = ord(name[0]) - ord("a")
    rank = int(name[1]) - 1
    return rank * 8 + file


def pick_move(pos, fr, to, **flags):
    moves = generate_legal_moves(pos)
    for m in moves:
        if m.from_sq == fr and m.to_sq == to:
            ok = True
            for k, v in flags.items():
                if getattr(m, k) != v:
                    ok = False
            if ok:
                return m
    raise AssertionError("Move not found")


def test_san_pawn_push():
    pos = parse_fen("8/8/8/8/8/8/4P3/4K3 w - - 0 1")
    m = pick_move(pos, sq("e2"), sq("e4"))
    assert move_to_san(pos, m) == "e4"


def test_san_pawn_capture():
    pos = parse_fen("8/8/8/3p4/4P3/8/8/4K3 w - - 0 1")
    m = pick_move(pos, sq("e4"), sq("d5"))
    assert move_to_san(pos, m) == "exd5"


def test_san_castle_kingside():
    pos = parse_fen("8/8/8/8/8/8/8/4K2R w K - 0 1")
    m = pick_move(pos, sq("e1"), sq("g1"), is_castle=True)
    assert move_to_san(pos, m) == "O-O"


def test_san_promotion_with_check_suffix():
    # white pawn promotes on a8 giving check to black king on h8 via new queen
    pos = parse_fen("7k/P7/8/8/8/8/8/4K3 w - - 0 1")
    # move returned is promo="?" so we construct a concrete move for SAN test
    m0 = pick_move(pos, sq("a7"), sq("a8"))
    # emulate user picking queen
    from engine.types import Move

    m = Move(from_sq=m0.from_sq, to_sq=m0.to_sq, promo="q")
    assert move_to_san(pos, m) == "a8=Q+"
