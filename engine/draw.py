from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from engine.types import Position


class DrawType(Enum):
    INSUFFICIENT_MATERIAL = auto()
    STALEMATE = auto()
    FIFTY_MOVE_CLAIM = auto()
    THREEFOLD_CLAIM = auto()


@dataclass(frozen=True)
class DrawStatus:
    auto_draw: DrawType | None
    claimable: set[DrawType]


def insufficient_material(pos: Position) -> bool:
    """
    True if no mating material exists:
    - K vs K
    - K+N vs K
    - K+B vs K
    - K+B vs K+B with bishops on same color (optional; we implement conservative: treat as insufficient only if same-color)
    We'll implement common cases.
    """
    pieces = [p for p in pos.board if p != "."]
    # remove kings
    rest = [p for p in pieces if p.lower() != "k"]
    if not rest:
        return True

    # Count minor pieces only
    allowed = {"n", "b"}
    if all(p.lower() in allowed for p in rest):
        # K+N vs K, K+B vs K, K+N+N vs K is NOT insufficient by strict rules? (cannot force mate, but FIDE: K+NN vs K is insufficient)
        # We'll treat K+NN vs K as insufficient as well.
        if len(rest) == 1:
            return True
        if len(rest) == 2 and all(p.lower() == "n" for p in rest):
            return True

        # bishops same color only (one bishop each side)
        if len(rest) == 2 and all(p.lower() == "b" for p in rest):
            # find bishop square colors
            bishops = []
            for sq, p in enumerate(pos.board):
                if p.lower() == "b":
                    r, f = divmod(sq, 8)
                    bishops.append((p, (r + f) % 2))
            if len(bishops) == 2 and bishops[0][1] == bishops[1][1]:
                return True

    return False


def fifty_move_claimable(pos: Position) -> bool:
    return pos.halfmove_clock >= 100  # 100 half-moves = 50 full moves


def threefold_claimable(repetition_count_current: int) -> bool:
    return repetition_count_current >= 3
