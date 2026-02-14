from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import chess

_FILES = "abcdefgh"


def _to_uci_square(x: int, y: int) -> str:
    # x=0 -> rank1, y=0 -> file a
    return f"{_FILES[y]}{x + 1}"


@dataclass
class SanHistory:
    sans: List[str] = field(default_factory=list)

    def reset(self) -> None:
        self.sans.clear()

    def push_from_fen_and_coords(
        self,
        fen_before_move: str,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        promotion: Optional[str] = None,
    ) -> str:
        uci = _to_uci_square(x1, y1) + _to_uci_square(x2, y2)
        if promotion:
            uci += promotion.lower()

        board = chess.Board(fen_before_move)
        move = chess.Move.from_uci(uci)

        san = board.san(move)
        board.push(move)

        self.sans.append(san)
        return san

    def formatted(self) -> str:
        # หลายบรรทัด: 1. e4 e5
        lines: List[str] = []
        for i in range(0, len(self.sans), 2):
            move_no = i // 2 + 1
            white = self.sans[i]
            black = self.sans[i + 1] if i + 1 < len(self.sans) else ""
            lines.append(f"{move_no}. {white}" + (f" {black}" if black else ""))
        return "\n".join(lines)