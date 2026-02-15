from chess_core.rules import (
    turn, SAN_HISTORY, compute_legal_hints_for, clear_legal_hints,
    apply_promotion, end_turn, check_for_check, check_for_checkmate
)
from chess_core.board import Board
from chess_core.square import EmptySquare
from chess_core.pieces import King, Queen, Rook, Bishop, Knight, Pawn

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

        # NEW: pending promotion state
        # tuple: (fen_before, x1, y1, x2, y2, iswhite)
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
        self.move_list_text = SAN_HISTORY.formatted()

    def ui_to_model(self, ui_row: int, ui_col: int):
        mx = 7 - ui_row
        my = ui_col

        if self.view_iswhite:
            return mx, my

        return 7 - mx, 7 - my

    def refresh_all(self):
        for sw in self._squares:
            sw.refresh()

    def click_model(self, mx, my):
        # ถ้ามี promotion ค้างอยู่: บล็อกการคลิกกระดาน
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

        # กดครั้งที่ 2 = พยายามเดิน
        result = turn(self.s_x, self.s_y, mx, my, self.iswhite)

        clear_legal_hints()

        # รีเซ็ต selection highlight
        self.selected = False
        Board.board[self.s_x][self.s_y].piece.selected = False
        Board.board[mx][my].piece.selected = False

        # ----- NEW: handle promotion pending -----
        if isinstance(result, tuple) and len(result) >= 1 and result[0] == "PROMOTION":
            _, fen_before, x1, y1, x2, y2, moved_iswhite = result
            self._pending_promotion = (fen_before, x1, y1, x2, y2, moved_iswhite)

            # เปิด popup ให้เลือก
            PromotionPopup(on_pick=self._finalize_promotion).open()

            self.refresh_all()
            return

        moved = bool(result)

        if moved:
            self.iswhite = not self.iswhite
            self.view_iswhite = self.iswhite  # flip ตามฝั่งเดิน

        self.move_list_text = SAN_HISTORY.formatted()
        self.refresh_all()

    def _finalize_promotion(self, choice: str) -> None:
        """
        choice: 'q','r','b','n'
        """
        if self._pending_promotion is None:
            return

        fen_before, x1, y1, x2, y2, moved_iswhite = self._pending_promotion
        self._pending_promotion = None

        # 1) เปลี่ยนตัวหมากบนกระดานตามที่เลือก
        apply_promotion(x2, y2, moved_iswhite, choice)

        # 2) push SAN โดยระบุ promotion
        SAN_HISTORY.push_from_fen_and_coords(
            fen_before_move=fen_before,
            x1=x1, y1=y1, x2=x2, y2=y2,
            promotion=choice,
        )

        # 3) end turn (reset en passant, etc.)
        end_turn(moved_iswhite)

        # 4) check/checkmate หลังโปรโมต (เพราะชิ้นที่โปรโมตมีผล)
        other_iswhite = not moved_iswhite
        if check_for_check(other_iswhite):
            if check_for_checkmate(other_iswhite):
                for i in range(64):
                    sq = Board.board[i // 8][i % 8]
                    if isinstance(sq.piece, King) and sq.piece.iswhite == other_iswhite:
                        sq.piece.selected = True

        # 5) flip side + update UI texts
        self.iswhite = not self.iswhite
        self.view_iswhite = self.iswhite

        self.move_list_text = SAN_HISTORY.formatted()
        self.refresh_all()


class Ui(BoxLayout):
    w, h = Window._get_size()
    ui_size_x = max(w, h) - min(w, h)
    ui_size_y = min(w, h)
    ui_pos_x = min(w, h)


class ChessApp(App):
    pass


ChessApp().run()