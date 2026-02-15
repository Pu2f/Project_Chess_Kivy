from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GameState:
    # halfmove_clock นับเป็น ply (ครึ่งตา) ตาม FEN
    halfmove_clock: int = 0
    # fullmove_number เริ่มที่ 1 และเพิ่มหลัง "ดำ" เดินจบ
    fullmove_number: int = 1

    # เกมจบแล้ว (draw/checkmate ฯลฯ)
    game_over: bool = False
    result_text: str = ""

    def reset(self) -> None:
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.game_over = False
        self.result_text = ""


GAME_STATE = GameState()