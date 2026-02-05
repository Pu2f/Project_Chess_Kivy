from dataclasses import dataclass

@dataclass(frozen=True)
class CastlingRights:
    wk: bool = True
    wq: bool = True
    bk: bool = True
    bq: bool = True

@dataclass(frozen=True)
class Move:
    from_sq: int
    to_sq: int
    promo: str | None = None  # "q","r","b","n" (lowercase for internal)
    is_castle: bool = False
    is_en_passant: bool = False

@dataclass
class Position:
    board: list[str]              # 64 chars
    side_to_move: str             # "w" / "b"
    castling: CastlingRights
    en_passant_sq: int | None     # square index or None
    halfmove_clock: int
    fullmove_number: int