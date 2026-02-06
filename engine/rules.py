from __future__ import annotations

from engine.types import Position, Move, CastlingRights

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
    attacks: set[int] = set()
    b = pos.board

    for from_sq, p in enumerate(b):
        if p == "." or not same_side(p, attacker_side):
            continue

        pr, pf = rf(from_sq)
        pl = p.lower()

        if pl == "p":
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


def _remove_castling_rights_for_move(pos: Position, move: Move) -> CastlingRights:
    """
    Update castling rights based on king/rook movement or rook capture.
    Assumes standard starting squares:
    White king e1, rooks a1/h1; Black king e8, rooks a8/h8.
    """
    c = pos.castling
    b = pos.board
    piece = b[move.from_sq]
    captured = b[move.to_sq]

    wk, wq, bk, bq = c.wk, c.wq, c.bk, c.bq

    # king moved
    if piece == "K":
        wk = False
        wq = False
    elif piece == "k":
        bk = False
        bq = False

    # rook moved from original squares
    if piece == "R":
        if move.from_sq == sq_of(0, 0):  # a1
            wq = False
        elif move.from_sq == sq_of(0, 7):  # h1
            wk = False
    elif piece == "r":
        if move.from_sq == sq_of(7, 0):  # a8
            bq = False
        elif move.from_sq == sq_of(7, 7):  # h8
            bk = False

    # rook captured on original squares
    if captured == "R":
        if move.to_sq == sq_of(0, 0):
            wq = False
        elif move.to_sq == sq_of(0, 7):
            wk = False
    elif captured == "r":
        if move.to_sq == sq_of(7, 0):
            bq = False
        elif move.to_sq == sq_of(7, 7):
            bk = False

    return CastlingRights(wk=wk, wq=wq, bk=bk, bq=bq)


def apply_move(pos: Position, move: Move) -> Position:
    """
    Apply a fully-specified move (including castle, en passant, promotion).
    """
    b = pos.board[:]
    piece = b[move.from_sq]
    target_before = b[move.to_sq]

    # clear en passant by default; may be set by pawn double push
    en_passant_sq = None

    # base move
    b[move.from_sq] = "."

    # en passant capture removes pawn behind target square
    if move.is_en_passant:
        tr, tf = rf(move.to_sq)
        cap_r = tr - 1 if pos.side_to_move == "w" else tr + 1
        cap_sq = sq_of(cap_r, tf)
        b[cap_sq] = "."

    # castling rook move
    if move.is_castle:
        # king destinations:
        # white: e1->g1 (rook h1->f1) or e1->c1 (rook a1->d1)
        # black: e8->g8 (rook h8->f8) or e8->c8 (rook a8->d8)
        if piece == "K" and move.to_sq == sq_of(0, 6):  # g1
            b[sq_of(0, 5)] = "R"
            b[sq_of(0, 7)] = "."
        elif piece == "K" and move.to_sq == sq_of(0, 2):  # c1
            b[sq_of(0, 3)] = "R"
            b[sq_of(0, 0)] = "."
        elif piece == "k" and move.to_sq == sq_of(7, 6):  # g8
            b[sq_of(7, 5)] = "r"
            b[sq_of(7, 7)] = "."
        elif piece == "k" and move.to_sq == sq_of(7, 2):  # c8
            b[sq_of(7, 3)] = "r"
            b[sq_of(7, 0)] = "."
        else:
            raise ValueError("Invalid castling move")

    # promotion
    if move.promo is not None:
        # promo stored as lowercase letter: q r b n
        promo = move.promo.lower()
        if pos.side_to_move == "w":
            b[move.to_sq] = promo.upper()
        else:
            b[move.to_sq] = promo
    else:
        b[move.to_sq] = piece

    # pawn double push sets en passant square
    if piece.lower() == "p":
        fr, ff = rf(move.from_sq)
        tr, tf = rf(move.to_sq)
        if ff == tf and abs(tr - fr) == 2:
            mid_r = (fr + tr) // 2
            en_passant_sq = sq_of(mid_r, ff)

    # castling rights update
    castling = _remove_castling_rights_for_move(pos, move)
    # if king castled, castling rights must be gone anyway (covered by king move)

    next_side = "b" if pos.side_to_move == "w" else "w"

    is_capture = (target_before != ".") or move.is_en_passant
    is_pawn = piece.lower() == "p"
    halfmove = 0 if (is_capture or is_pawn) else (pos.halfmove_clock + 1)
    fullmove = pos.fullmove_number + (1 if next_side == "w" else 0)

    return Position(
        board=b,
        side_to_move=next_side,
        castling=castling,
        en_passant_sq=en_passant_sq,
        halfmove_clock=halfmove,
        fullmove_number=fullmove,
    )


def _add_pawn_promotions(
    side: str, from_sq: int, to_sq: int, is_capture: bool = False
) -> list[Move]:
    # mark as promo-needed by using promo="?" (UI จะขอเลือก)
    # later we will generate concrete promo moves too, but UI flow wants "?"
    return [Move(from_sq, to_sq, promo="?", is_en_passant=False, is_castle=False)]


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
            promo_rank = 7 if side == "w" else 0

            # single push
            tr = fr + dr
            if on_board(tr, ff):
                to_sq = sq_of(tr, ff)
                if b[to_sq] == ".":
                    if tr == promo_rank:
                        moves.extend(_add_pawn_promotions(side, from_sq, to_sq))
                    else:
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
                    if tr == promo_rank:
                        moves.extend(
                            _add_pawn_promotions(side, from_sq, to_sq, is_capture=True)
                        )
                    else:
                        moves.append(Move(from_sq, to_sq))

            # en passant
            if pos.en_passant_sq is not None:
                ep_r, ep_f = rf(pos.en_passant_sq)
                if ep_r == fr + dr and abs(ep_f - ff) == 1:
                    # target square equals ep square; capture pawn behind it
                    moves.append(Move(from_sq, pos.en_passant_sq, is_en_passant=True))

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

            # castling pseudo-legal: check empties + rights; check squares attacked in legal filter
            moves.extend(_castle_moves_pseudo(pos))

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


def _castle_moves_pseudo(pos: Position) -> list[Move]:
    b = pos.board
    side = pos.side_to_move
    res: list[Move] = []

    opp = "b" if side == "w" else "w"
    attacked = attacked_by_side(pos, opp)

    def empty(sq: int) -> bool:
        return b[sq] == "."

    if side == "w":
        king_from = sq_of(0, 4)  # e1
        if b[king_from] != "K":
            return res

        # cannot castle out of check
        if king_from in attacked:
            return res

        # kingside: e1->g1, squares f1 g1 empty, f1 g1 not attacked, rook at h1
        if (
            pos.castling.wk
            and b[sq_of(0, 7)] == "R"
            and empty(sq_of(0, 5))
            and empty(sq_of(0, 6))
        ):
            if sq_of(0, 5) not in attacked and sq_of(0, 6) not in attacked:
                res.append(Move(king_from, sq_of(0, 6), is_castle=True))

        # queenside: e1->c1, squares d1 c1 b1 empty, d1 c1 not attacked, rook at a1
        if (
            pos.castling.wq
            and b[sq_of(0, 0)] == "R"
            and empty(sq_of(0, 3))
            and empty(sq_of(0, 2))
            and empty(sq_of(0, 1))
        ):
            if sq_of(0, 3) not in attacked and sq_of(0, 2) not in attacked:
                res.append(Move(king_from, sq_of(0, 2), is_castle=True))

    else:
        king_from = sq_of(7, 4)  # e8
        if b[king_from] != "k":
            return res

        if king_from in attacked:
            return res

        if (
            pos.castling.bk
            and b[sq_of(7, 7)] == "r"
            and empty(sq_of(7, 5))
            and empty(sq_of(7, 6))
        ):
            if sq_of(7, 5) not in attacked and sq_of(7, 6) not in attacked:
                res.append(Move(king_from, sq_of(7, 6), is_castle=True))

        if (
            pos.castling.bq
            and b[sq_of(7, 0)] == "r"
            and empty(sq_of(7, 3))
            and empty(sq_of(7, 2))
            and empty(sq_of(7, 1))
        ):
            if sq_of(7, 3) not in attacked and sq_of(7, 2) not in attacked:
                res.append(Move(king_from, sq_of(7, 2), is_castle=True))

    return res


def generate_legal_moves(pos: Position) -> list[Move]:
    legal: list[Move] = []
    side = pos.side_to_move

    for m in generate_pseudo_legal_moves(pos):
        new_pos = apply_move(pos, m)

        # after move, side_to_move switched; check if mover's king is in check
        mover = side
        if not is_in_check(new_pos, mover):
            legal.append(m)

    return legal
