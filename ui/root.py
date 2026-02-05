from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty

from ui.board import BoardGrid
from ui.sidepanel import SidePanel
from engine.game import ChessGame


class ChessRoot(BoxLayout):
    status_text = StringProperty("Ready")
    highlight_enabled = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", **kwargs)

        self.game = ChessGame()
        self.board = BoardGrid(on_square=self.on_square)  # callback #1/#2 จะอยู่ที่ปุ่ม
        self.panel = SidePanel(
            on_new_game=self.on_new_game,                 # callback #3
            on_undo=self.on_undo,                         # callback #4
            on_flip=self.on_flip,                         # callback #5
            on_hint=self.on_hint,                         # callback #6
            on_toggle_highlight=self.on_toggle_highlight, # callback #7
            on_load_fen=self.on_load_fen,                 # callback #8
        )

        self.add_widget(self.board)
        self.add_widget(self.panel)

        self.selected = None
        self.flipped = False

        self.sync_ui()

    def sync_ui(self):
        self.board.set_position(self.game.position, flipped=self.flipped)

        self.panel.set_turn("White" if self.game.position.side_to_move == "w" else "Black")
        self.panel.set_status(self.game.status_string())
        self.panel.set_fen(self.game.to_fen())
        self.panel.set_moves(self.game.move_san_list())

        # ไฮไลต์ selection + legal moves
        if self.highlight_enabled and self.selected is not None:
            legal = self.game.legal_moves_from(self.selected)
            self.board.set_highlights(self.selected, [m.to_sq for m in legal])
        else:
            self.board.clear_highlights()

    def on_square(self, sq):
        # เลือกต้นทาง / เลือกปลายทาง
        if self.selected is None:
            # เลือกหมากเฉพาะของฝ่ายที่เดิน
            if self.game.can_select(sq):
                self.selected = sq
        else:
            if sq == self.selected:
                self.selected = None
            else:
                result = self.game.try_move(self.selected, sq)
                if result == "promotion_needed":
                    # โปรโมชัน: ให้เลือกจาก panel (ง่ายสุด: Queen auto ก็ได้ แต่เราทำให้เลือก)
                    self.panel.open_promotion_dialog(self.game.position.side_to_move)
                else:
                    self.selected = None

        self.sync_ui()

    def on_new_game(self):
        self.game.reset()
        self.selected = None
        self.sync_ui()

    def on_undo(self):
        self.game.undo()
        self.selected = None
        self.sync_ui()

    def on_flip(self):
        self.flipped = not self.flipped
        self.sync_ui()

    def on_hint(self):
        # hint แบบสุภาพ: แสดง legal moves ของตัวที่เลือก หรือแนะนำหนึ่งเดินแบบง่าย ๆ
        if self.selected is None:
            self.panel.flash_message("Select a piece first.")
        else:
            self.panel.flash_message(f"{len(self.game.legal_moves_from(self.selected))} legal moves.")
        self.sync_ui()

    def on_toggle_highlight(self, enabled: bool):
        self.highlight_enabled = enabled
        self.sync_ui()

    def on_load_fen(self, fen: str):
        ok, msg = self.game.load_fen(fen)
        self.panel.flash_message(msg)
        if ok:
            self.selected = None
        self.sync_ui()

    def on_key_down(self, _window, key, scancode, codepoint, modifiers):
        # Ctrl+Z undo, N new, F flip
        if "ctrl" in modifiers and codepoint.lower() == "z":
            self.on_undo()
            return True
        if codepoint.lower() == "n":
            self.on_new_game()
            return True
        if codepoint.lower() == "f":
            self.on_flip()
            return True
        return False

    def tick(self, _dt):
        # ไว้ทำ status refresh / animation; ตอนนี้ใช้เป็น noop เบา ๆ
        return True