from chess_core.rules import (
    turn,
    SAN_HISTORY,
    compute_legal_hints_for,
    clear_legal_hints,
    apply_promotion,
    end_turn,
    check_for_check,
    check_for_checkmate,
)
from chess_core.board import Board
from chess_core.square import EmptySquare
from chess_core.pieces import King, Queen, Rook, Bishop, Knight, Pawn
from chess_core.game_state import GAME_STATE

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import StringProperty

from chess_ui.font_piece_renderer import ChessCasesRenderer
from chess_ui.square_widget import SquareWidget
from chess_ui.promotion_popup import PromotionPopup

# init model
Board.create_board()


class ChessGame(BoxLayout):
    pass


def piece_to_letter(piece) -> str:
    if isinstance(piece, EmptySquare):
        return "."
    if isinstance(piece, King):
        return "K" if piece.iswhite else "k"
    if isinstance(piece, Queen):
        return "Q" if piece.iswhite else "q"
    if isinstance(piece, Rook):
        return "R" if piece.iswhite else "r"
    if isinstance(piece, Bishop):
        return "B" if piece.iswhite else "b"
    if isinstance(piece, Knight):
        return "N" if piece.iswhite else "n"
    if isinstance(piece, Pawn):
        return "P" if piece.iswhite else "p"
    return "."


class BoardGrid(GridLayout):
    move_list_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 8

        self.iswhite = True
        self.view_iswhite = self.iswhite

        self.selected = False
        self.s_x = None
        self.s_y = None

        # pending promotion state
        self._pending_promotion = None

        w, h = Window._get_size()
        self.board_size = h if w > h else w
        self.square_size = int(self.board_size / 8)

        self.renderer = ChessCasesRenderer()
        self.renderer.ensure_cache(self.square_size)

        self._squares = []
        for ui_row in range(8):
            for ui_col in range(8):
                sw = SquareWidget(
                    ui_x=ui_row,
                    ui_y=ui_col,
                    ui_to_model=self.ui_to_model,
                    on_click_model=self.click_model,
                    board_getter=lambda: Board.board,
                    piece_letter_getter=piece_to_letter,
                    renderer=self.renderer,
                )
                self._squares.append(sw)
                self.add_widget(sw)

        self.refresh_all()
        self._update_move_list()

    def ui_to_model(self, ui_row: int, ui_col: int):
        mx = 7 - ui_row
        my = ui_col

        if self.view_iswhite:
            return mx, my

        return 7 - mx, 7 - my

    def refresh_all(self):
        for sw in self._squares:
            sw.refresh()

    def _update_move_list(self) -> None:
        base = SAN_HISTORY.formatted()
        if GAME_STATE.result_text:
            self.move_list_text = (
                base + ("\n\n" if base else "") + GAME_STATE.result_text
            )
        else:
            self.move_list_text = base

    def click_model(self, mx, my):
        # ล็อกเกมเมื่อจบ (รวมเสมอ)
        if GAME_STATE.game_over:
            return

        # promotion ค้างอยู่: บล็อกการคลิกกระดาน
        if self._pending_promotion is not None:
            return

        if not self.selected:
            self.s_x = mx
            self.s_y = my
            self.selected = True

            Board.board[mx][my].piece.selected = True
            compute_legal_hints_for(mx, my, self.iswhite)

            self.refresh_all()
            return

        result = turn(self.s_x, self.s_y, mx, my, self.iswhite)

        clear_legal_hints()

        self.selected = False
        Board.board[self.s_x][self.s_y].piece.selected = False
        Board.board[mx][my].piece.selected = False

        # promotion pending
        if isinstance(result, tuple) and result and result[0] == "PROMOTION":
            _, fen_before, x1, y1, x2, y2, moved_iswhite = result
            self._pending_promotion = (fen_before, x1, y1, x2, y2, moved_iswhite)
            PromotionPopup(on_pick=self._finalize_promotion).open()
            self.refresh_all()
            return

        # draw
        if isinstance(result, tuple) and result and result[0] == "DRAW":
            self._update_move_list()
            self.refresh_all()
            return

        moved = bool(result)
        if moved:
            self.iswhite = not self.iswhite
            self.view_iswhite = self.iswhite

        self._update_move_list()
        self.refresh_all()

    def _finalize_promotion(self, choice: str) -> None:
        if self._pending_promotion is None or GAME_STATE.game_over:
            return

        fen_before, x1, y1, x2, y2, moved_iswhite = self._pending_promotion
        self._pending_promotion = None

        apply_promotion(x2, y2, moved_iswhite, choice)

        SAN_HISTORY.push_from_fen_and_coords(
            fen_before_move=fen_before,
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            promotion=choice,
        )

        # clocks: promotion = pawn move
        GAME_STATE.halfmove_clock = 0
        if not moved_iswhite:
            GAME_STATE.fullmove_number += 1

        end_turn(moved_iswhite)

        other_iswhite = not moved_iswhite
        if check_for_check(other_iswhite):
            if check_for_checkmate(other_iswhite):
                for i in range(64):
                    sq = Board.board[i // 8][i % 8]
                    if isinstance(sq.piece, King) and sq.piece.iswhite == other_iswhite:
                        sq.piece.selected = True

        # draw check after promotion
        import chess
        from chess_core.fen import to_fen

        fen_after = to_fen(
            side_to_move_iswhite=other_iswhite,
            halfmove_clock=GAME_STATE.halfmove_clock,
            fullmove_number=GAME_STATE.fullmove_number,
        )
        b = chess.Board(fen_after)

        reason = None
        if b.is_stalemate():
            reason = "Draw by stalemate"
        elif b.can_claim_threefold_repetition():
            reason = "Draw by threefold repetition (claim)"
        elif b.can_claim_fifty_moves():
            reason = "Draw by 50-move rule (claim)"

        if reason:
            GAME_STATE.game_over = True
            GAME_STATE.result_text = reason

        # flip side (ถ้าไม่เสมอ)
        if not GAME_STATE.game_over:
            self.iswhite = not self.iswhite
            self.view_iswhite = self.iswhite

        self._update_move_list()
        self.refresh_all()


class Ui(BoxLayout):
    w, h = Window._get_size()
    ui_size_x = max(w, h) - min(w, h)
    ui_size_y = min(w, h)
    ui_pos_x = min(w, h)


class ChessApp(App):
    pass


ChessApp().run()
