from __future__ import annotations

from dataclasses import dataclass

from engine.fen import START_FEN, parse_fen, to_fen
from engine.types import Position, Move
from engine.rules import generate_legal_moves, is_in_check, apply_move
from engine.zobrist import hash_position
from engine.draw import (
    DrawStatus,
    DrawType,
    insufficient_material,
    fifty_move_claimable,
    threefold_claimable,
)
from engine.san import move_to_san


@dataclass
class UndoState:
    position: Position
    san: str
    rep_hash: int


@dataclass
class GameEnd:
    kind: str  # "checkmate" | "stalemate" | "draw" | "ongoing"
    message: str


class ChessGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.position = parse_fen(START_FEN)
        self.history: list[UndoState] = []
        self.san_moves: list[str] = []
        self.pending_promotion: Move | None = None

        self.repetition: dict[int, int] = {}
        self._track_repetition(self.position)

    def _track_repetition(self, pos: Position):
        h = hash_position(pos)
        self.repetition[h] = self.repetition.get(h, 0) + 1

    def _untrack_repetition(self, pos: Position):
        h = hash_position(pos)
        cur = self.repetition.get(h, 0)
        if cur <= 1:
            self.repetition.pop(h, None)
        else:
            self.repetition[h] = cur - 1

    def to_fen(self) -> str:
        return to_fen(self.position)

    def load_fen(self, fen: str):
        try:
            self.position = parse_fen(fen)
            self.history.clear()
            self.san_moves.clear()
            self.pending_promotion = None
            self.repetition.clear()
            self._track_repetition(self.position)
            return True, "FEN loaded."
        except Exception as e:
            return False, f"Bad FEN: {e}"

    def move_san_list(self) -> list[str]:
        """
        Return pretty move list like:
        1. e4
        1... e5
        2. Nf3
        """
        out = []
        for i, san in enumerate(self.san_moves):
            move_no = (i // 2) + 1
            if i % 2 == 0:
                out.append(f"{move_no}. {san}")
            else:
                out.append(f"{move_no}... {san}")
        return out

    def can_select(self, sq: int) -> bool:
        p = self.position.board[sq]
        if p == ".":
            return False
        return (self.position.side_to_move == "w" and p.isupper()) or (
            self.position.side_to_move == "b" and p.islower()
        )

    def legal_moves(self) -> list[Move]:
        return generate_legal_moves(self.position)

    def legal_moves_from(self, from_sq: int):
        return [m for m in self.legal_moves() if m.from_sq == from_sq]

    def end_state(self) -> GameEnd:
        if insufficient_material(self.position):
            return GameEnd("draw", "Draw: insufficient material.")

        moves = self.legal_moves()
        in_check = is_in_check(self.position, self.position.side_to_move)

        if not moves and in_check:
            winner = "Black" if self.position.side_to_move == "w" else "White"
            return GameEnd("checkmate", f"Checkmate! {winner} wins.")
        if not moves and not in_check:
            return GameEnd("stalemate", "Draw: stalemate.")
        return GameEnd("ongoing", "OK" if not in_check else "Check!")

    def draw_status(self) -> DrawStatus:
        auto = None
        claimable: set[DrawType] = set()

        end = self.end_state()
        if end.kind == "stalemate":
            auto = DrawType.STALEMATE
        elif end.kind == "draw" and "insufficient" in end.message.lower():
            auto = DrawType.INSUFFICIENT_MATERIAL

        if fifty_move_claimable(self.position):
            claimable.add(DrawType.FIFTY_MOVE_CLAIM)

        h = hash_position(self.position)
        rep_count = self.repetition.get(h, 0)
        if threefold_claimable(rep_count):
            claimable.add(DrawType.THREEFOLD_CLAIM)

        return DrawStatus(auto_draw=auto, claimable=claimable)

    def claim_draw(self) -> tuple[bool, str]:
        ds = self.draw_status()
        if ds.auto_draw is not None:
            return True, "Draw confirmed."

        reasons = []
        if DrawType.FIFTY_MOVE_CLAIM in ds.claimable:
            reasons.append("50-move rule")
        if DrawType.THREEFOLD_CLAIM in ds.claimable:
            reasons.append("threefold repetition")

        if not reasons:
            return False, "No claimable draw right now."
        return True, "Draw claimed: " + " & ".join(reasons) + "."

    def status_string(self) -> str:
        end = self.end_state()
        if end.kind == "ongoing":
            ds = self.draw_status()
            extras = []
            if DrawType.FIFTY_MOVE_CLAIM in ds.claimable:
                extras.append("50-move claimable")
            if DrawType.THREEFOLD_CLAIM in ds.claimable:
                extras.append("3x repetition claimable")
            if extras:
                return f"{end.message} ({', '.join(extras)})"
            return end.message
        return end.message

    def try_move(self, from_sq: int, to_sq: int):
        if self.pending_promotion is not None:
            return "promotion_pending"

        if self.end_state().kind in ("checkmate", "stalemate", "draw"):
            return "game_over"

        candidates = [m for m in self.legal_moves_from(from_sq) if m.to_sq == to_sq]
        if not candidates:
            return "illegal"

        m = candidates[0]

        if m.promo == "?":
            self.pending_promotion = m
            return "promotion_needed"

        self.apply_move(m)
        return "ok"

    def promote(self, piece_letter: str):
        if self.pending_promotion is None:
            return False

        p = piece_letter.lower().strip()
        if p not in ("q", "r", "b", "n"):
            return False

        m = Move(
            from_sq=self.pending_promotion.from_sq,
            to_sq=self.pending_promotion.to_sq,
            promo=p,
            is_castle=self.pending_promotion.is_castle,
            is_en_passant=self.pending_promotion.is_en_passant,
        )
        self.pending_promotion = None
        self.apply_move(m)
        return True

    def apply_move(self, move: Move):
        rep_hash_before = hash_position(self.position)
        san = move_to_san(self.position, move)

        self.history.append(
            UndoState(position=self.position, san=san, rep_hash=rep_hash_before)
        )

        self.position = apply_move(self.position, move)
        self._track_repetition(self.position)

        self.san_moves.append(san)

    def undo(self):
        if not self.history:
            return

        self._untrack_repetition(self.position)

        st = self.history.pop()
        self.position = st.position
        if self.san_moves:
            self.san_moves.pop()
        self.pending_promotion = None
