from dataclasses import dataclass

from engine.fen import START_FEN, parse_fen, to_fen
from engine.types import Position, Move
from engine.rules import generate_legal_moves, is_in_check


@dataclass
class UndoState:
    position: Position
    move_san: str


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
        # โครง: engine เต็มจะเติม checkmate/stalemate/draw
        chk = is_in_check(self.position, self.position.side_to_move)
        return "Check!" if chk else "OK"

    def move_san_list(self) -> list[str]:
        return list(self.san_moves)

    def can_select(self, sq: int) -> bool:
        p = self.position.board[sq]
        if p == ".":
            return False
        return (self.position.side_to_move == "w" and p.isupper()) or (self.position.side_to_move == "b" and p.islower())

    def legal_moves_from(self, from_sq: int):
        return [m for m in generate_legal_moves(self.position) if m.from_sq == from_sq]

    def try_move(self, from_sq: int, to_sq: int):
        moves = self.legal_moves_from(from_sq)
        candidates = [m for m in moves if m.to_sq == to_sq]

        if not candidates:
            return "illegal"

        m = candidates[0]
        # promotion: ต้องเลือก promo
        if m.promo is not None and m.promo == "?":
            self.pending_promotion = m
            return "promotion_needed"

        self.apply_move(m)
        return "ok"

    def apply_move(self, move: Move):
        # NOTE: โครง; rules.py จะมี apply ที่ถูกต้องครบกติกา + undo data
        self.history.append(UndoState(position=self.position, move_san="(todo)"))
        self.position = self._apply_naive(move)
        self.san_moves.append("(todo)")

    def _apply_naive(self, move: Move) -> Position:
        # แค่ทำให้เดินได้เพื่อ UI; engine เต็มจะ replace
        pos = self.position
        b = pos.board[:]
        b[move.to_sq] = b[move.from_sq]
        b[move.from_sq] = "."
        stm = "b" if pos.side_to_move == "w" else "w"
        return Position(
            board=b,
            side_to_move=stm,
            castling=pos.castling,
            en_passant_sq=None,
            halfmove_clock=pos.halfmove_clock + 1,
            fullmove_number=pos.fullmove_number + (1 if stm == "w" else 0),
        )

    def undo(self):
        if not self.history:
            return
        st = self.history.pop()
        self.position = st.position
        if self.san_moves:
            self.san_moves.pop()
        self.pending_promotion = None