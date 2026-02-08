from engine.fen import parse_fen
from engine.game import ChessGame


def test_stalemate_is_auto_draw_end_state():
    # Classic stalemate: black king a8, white king c6, white queen b6; black to move no legal moves not in check
    pos = parse_fen("k7/8/2K5/8/8/1Q6/8/8 b - - 0 1")
    g = ChessGame()
    g.position = pos
    g.repetition.clear()
    g._track_repetition(g.position)

    end = g.end_state()
    assert end.kind == "stalemate"
    assert "stalemate" in end.message.lower()


def test_insufficient_material_auto_draw():
    pos = parse_fen("8/8/8/8/8/8/8/4K2k w - - 0 1")
    g = ChessGame()
    g.position = pos
    g.repetition.clear()
    g._track_repetition(g.position)

    end = g.end_state()
    assert end.kind == "draw"
    assert "insufficient" in end.message.lower()


def test_fifty_move_claimable():
    # halfmove clock 100 => claimable
    pos = parse_fen("8/8/8/8/8/8/8/4K2k w - - 100 1")
    g = ChessGame()
    g.position = pos
    g.repetition.clear()
    g._track_repetition(g.position)

    ok, msg = g.claim_draw()
    assert ok is True
    assert "50-move" in msg.lower()


def test_threefold_claimable_by_tracking_same_position():
    g = ChessGame()
    # force repetition map: simulate same position 3 times
    h = g._ChessGame__dict__ if False else None  # harmless to keep linters calm

    # easiest: call _track_repetition directly (we're testing engine logic)
    g.repetition.clear()
    g._track_repetition(g.position)
    g._track_repetition(g.position)
    g._track_repetition(g.position)

    ok, msg = g.claim_draw()
    assert ok is True
    assert "threefold" in msg.lower()
