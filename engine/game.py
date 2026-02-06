from dataclasses import dataclass

from engine.fen import START_FEN, parse_fen, to_fen
from engine.types import Position, Move
from engine.rules import generate_legal_moves, is_in_check, apply_move_basic


@dataclass
class UndoState:
    position: Position
    san: str


class ChessGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.position = parse_fen(START_FEN)
        self.history: list[UndoState] = []
        self.san_moves: list[str] = []
        self.pending_promotion: Move | None = None

    def to_fen(self) -> str:
        return to_fen(self.position)

    def load_fen(self, fen: str):
        try:
            self.position = parse_fen(fen)
            self.history.clear()
            self.san_moves.clear()
            self.pending_promotion = None
            return True, "FEN loaded."
        except Exception as e:
            return False, f"Bad FEN: {e}"

    def status_string(self) -> str:
        chk = is_in_check(self.position, self.position.side_to_move)
        return "Check!" if chk else "OK"

    def move_san_list(self) -> list[str]:
        return list(self.san_moves)

    def can_select(self, sq: int) -> bool:
        p = self.position.board[sq]
        if p == ".":
            return False
        return (self.position.side_to_move == "w" and p.isupper()) or (
            self.position.side_to_move == "b" and p.islower()
        )

    def legal_moves_from(self, from_sq: int):
        return [m for m in generate_legal_moves(self.position) if m.from_sq == from_sq]

    def try_move(self, from_sq: int, to_sq: int):
        candidates = [m for m in self.legal_moves_from(from_sq) if m.to_sq == to_sq]
        if not candidates:
            return "illegal"

        m = candidates[0]

        # promotion later
        if m.promo is not None and m.promo == "?":
            self.pending_promotion = m
            return "promotion_needed"

        self.apply_move(m)
        return "ok"

    def apply_move(self, move: Move):
        self.history.append(UndoState(position=self.position, san="..."))
        self.position = apply_move_basic(self.position, move)
        self.san_moves.append("...")  # SAN later

    def undo(self):
        if not self.history:
            return
        st = self.history.pop()
        self.position = st.position
        if self.san_moves:
            self.san_moves.pop()
        self.pending_promotion = None
