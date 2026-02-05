from engine.types import Position, CastlingRights

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

def parse_fen(fen: str) -> Position:
    parts = fen.strip().split()
    if len(parts) != 6:
        raise ValueError("FEN must have 6 fields")

    board_part, stm, castling_part, ep_part, halfmove, fullmove = parts
    rows = board_part.split("/")
    if len(rows) != 8:
        raise ValueError("FEN board must have 8 ranks")

    board = []
    for r in rows:
        for ch in r:
            if ch.isdigit():
                board.extend(["."] * int(ch))
            else:
                board.append(ch)
    if len(board) != 64:
        raise ValueError("FEN board must expand to 64 squares")

    castling = CastlingRights(
        wk="K" in castling_part,
        wq="Q" in castling_part,
        bk="k" in castling_part,
        bq="q" in castling_part,
    )

    ep = None
    if ep_part != "-":
        file = ord(ep_part[0]) - ord("a")
        rank = int(ep_part[1]) - 1
        ep = rank * 8 + file

    return Position(
        board=board,
        side_to_move=stm,
        castling=castling,
        en_passant_sq=ep,
        halfmove_clock=int(halfmove),
        fullmove_number=int(fullmove),
    )

def to_fen(pos: Position) -> str:
    rows = []
    for rank in range(7, -1, -1):
        empty = 0
        s = ""
        for file in range(8):
            p = pos.board[rank * 8 + file]
            if p == ".":
                empty += 1
            else:
                if empty:
                    s += str(empty)
                    empty = 0
                s += p
        if empty:
            s += str(empty)
        rows.append(s)

    cast = ""
    cast += "K" if pos.castling.wk else ""
    cast += "Q" if pos.castling.wq else ""
    cast += "k" if pos.castling.bk else ""
    cast += "q" if pos.castling.bq else ""
    if cast == "":
        cast = "-"

    ep = "-"
    if pos.en_passant_sq is not None:
        f = pos.en_passant_sq % 8
        r = pos.en_passant_sq // 8
        ep = f"{chr(ord('a')+f)}{r+1}"

    return f"{'/'.join(rows)} {pos.side_to_move} {cast} {ep} {pos.halfmove_clock} {pos.fullmove_number}"