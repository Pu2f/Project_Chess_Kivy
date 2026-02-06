from engine.fen import parse_fen
from engine.rules import generate_legal_moves, apply_move


def sq(name: str) -> int:
    file = ord(name[0]) - ord("a")
    rank = int(name[1]) - 1
    return rank * 8 + file


def has_move(moves, fr, to, *, castle=False, ep=False, promo=None):
    for m in moves:
        if m.from_sq == fr and m.to_sq == to:
            if castle and not m.is_castle:
                continue
            if ep and not m.is_en_passant:
                continue
            if promo is not None and m.promo != promo:
                continue
            return True
    return False


def test_white_kingside_castle_available():
    # clear pieces between king and rook, and no checks
    pos = parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1")
    moves = generate_legal_moves(pos)
    assert has_move(moves, sq("e1"), sq("g1"), castle=True)


def test_castle_not_allowed_through_check():
    # black rook attacks f1 so castling should be illegal
    pos = parse_fen("4k2r/8/8/8/8/8/5r2/4K2R w K - 0 1")
    moves = generate_legal_moves(pos)
    assert not has_move(moves, sq("e1"), sq("g1"), castle=True)


def test_en_passant_generation_and_apply():
    # scenario: white pawn e5, black pawn d7 ready to double push to d5, then ep possible
    pos = parse_fen("8/3p4/8/4P3/8/8/8/4K3 b - - 0 1")
    # black plays d7->d5
    m1 = [
        m
        for m in generate_legal_moves(pos)
        if m.from_sq == sq("d7") and m.to_sq == sq("d5")
    ][0]
    pos2 = apply_move(pos, m1)
    assert pos2.en_passant_sq == sq("d6")
    # white has e5xd6 en passant
    moves2 = generate_legal_moves(pos2)
    assert has_move(moves2, sq("e5"), sq("d6"), ep=True)


def test_promotion_is_marked_as_needed():
    pos = parse_fen("8/4P3/8/8/8/8/8/4K3 w - - 0 1")
    moves = generate_legal_moves(pos)
    assert has_move(moves, sq("e7"), sq("e8"), promo="?")
