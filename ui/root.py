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
        self.board = BoardGrid(on_square=self.on_square)
        self.panel = SidePanel(
            on_new_game=self.on_new_game,
            on_undo=self.on_undo,
            on_flip=self.on_flip,
            on_hint=self.on_hint,
            on_toggle_highlight=self.on_toggle_highlight,
            on_load_fen=self.on_load_fen,
            on_promotion_choice=self.on_promotion_choice,
            on_claim_draw=self.on_claim_draw,  # NEW
        )

        self.add_widget(self.board)
        self.add_widget(self.panel)

        self.selected = None
        self.flipped = False

        self.sync_ui()

    def sync_ui(self):
        self.board.set_position(self.game.position, flipped=self.flipped)
        self.panel.set_turn(
            "White" if self.game.position.side_to_move == "w" else "Black"
        )
        self.panel.set_status(self.game.status_string())
        self.panel.set_fen(self.game.to_fen())
        self.panel.set_moves(self.game.move_san_list())

        if self.highlight_enabled and self.selected is not None:
            legal = self.game.legal_moves_from(self.selected)
            self.board.set_highlights(self.selected, [m.to_sq for m in legal])
        else:
            self.board.clear_highlights()

    def on_square(self, sq):
        if self.game.pending_promotion is not None:
            self.panel.flash_message("Pick promotion piece first.")
            return

        if self.game.end_state().kind != "ongoing":
            self.panel.flash_message("Game over. Start a new game.")
            self.sync_ui()
            return

        if self.selected is None:
            if self.game.can_select(sq):
                self.selected = sq
        else:
            if sq == self.selected:
                self.selected = None
            else:
                result = self.game.try_move(self.selected, sq)
                if result == "promotion_needed":
                    self.panel.open_promotion_dialog(self.game.position.side_to_move)
                elif result == "game_over":
                    self.panel.flash_message("Game over.")
                self.selected = None

        self.sync_ui()

    def on_promotion_choice(self, piece_letter: str):
        ok = self.game.promote(piece_letter)
        self.panel.flash_message("Promoted." if ok else "Promotion failed.")
        self.sync_ui()

    def on_claim_draw(self):
        ok, msg = self.game.claim_draw()
        # อารมณ์ขันนิด: claim ไม่ได้ = “ยังไม่ถึงเวลา”
        title = "Draw Claim" if ok else "Nope"
        self.panel.open_info_popup(title, msg)
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
        if self.selected is None:
            self.panel.flash_message("Select a piece first.")
        else:
            self.panel.flash_message(
                f"{len(self.game.legal_moves_from(self.selected))} legal moves."
            )
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
        if "ctrl" in modifiers and codepoint.lower() == "z":
            self.on_undo()
            return True
        if codepoint.lower() == "n":
            self.on_new_game()
            return True
        if codepoint.lower() == "f":
            self.on_flip()
            return True
        if codepoint.lower() == "d":
            self.on_claim_draw()
            return True
        return False

    def tick(self, _dt):
        return True
