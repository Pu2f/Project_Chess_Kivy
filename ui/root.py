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
            on_claim_draw=self.on_claim_draw,
        )

        self.add_widget(self.board)
        self.add_widget(self.panel)

        self.selected = None
        self.flipped = False
        self._last_end_kind = None

        # --- Chess clock state (NEW) ---
        self.initial_time = 5 * 60  # 5 minutes per side
        self.white_time = float(self.initial_time)
        self.black_time = float(self.initial_time)
        self._flag_fell = False
        # -------------------------------

        self.sync_ui()

    def _is_game_over(self) -> bool:
        if self._flag_fell:
            return True
        return self.game.end_state().kind in ("checkmate", "stalemate", "draw")

    def _maybe_show_end_popup(self):
        # if time flag fell, show that result (priority)
        if self._flag_fell:
            return

        end = self.game.end_state()
        if self._last_end_kind != end.kind:
            self._last_end_kind = end.kind
            if end.kind in ("checkmate", "stalemate", "draw"):
                self.panel.open_info_popup("Game Over", end.message)

    def _check_time_flag(self):
        if self._flag_fell:
            return
        if self.white_time <= 0:
            self._flag_fell = True
            self.panel.open_info_popup("Time", "White lost on time.")
        elif self.black_time <= 0:
            self._flag_fell = True
            self.panel.open_info_popup("Time", "Black lost on time.")

    def sync_ui(self):
        self.board.set_position(self.game.position, flipped=self.flipped)
        self.panel.set_turn("White" if self.game.position.side_to_move == "w" else "Black")
        self.panel.set_status(self.game.status_string())
        self.panel.set_fen(self.game.to_fen())
        self.panel.set_moves(self.game.move_san_list())

        # update clocks (NEW)
        self.panel.set_clocks(self.white_time, self.black_time)

        game_over = self._is_game_over()
        self.panel.set_game_over_mode(game_over)

        if game_over:
            self.selected = None
            self.board.clear_highlights()
        else:
            if self.highlight_enabled and self.selected is not None:
                legal = self.game.legal_moves_from(self.selected)
                self.board.set_highlights(self.selected, [m.to_sq for m in legal])
            else:
                self.board.clear_highlights()

        self._maybe_show_end_popup()

    def on_square(self, sq):
        if self.game.pending_promotion is not None:
            self.panel.flash_message("Pick promotion piece first.")
            return

        if self._is_game_over():
            self.panel.flash_message("Game over. Hit NEW GAME.")
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
                elif result == "illegal":
                    self.panel.flash_message("Illegal move. Nice try, though.")
                self.selected = None

        self.sync_ui()

    def on_promotion_choice(self, piece_letter: str):
        ok = self.game.promote(piece_letter)
        self.panel.flash_message("Promoted." if ok else "Promotion failed.")
        self.sync_ui()

    def on_claim_draw(self):
        ok, msg = self.game.claim_draw()
        title = "Draw Claim" if ok else "Nope"
        self.panel.open_info_popup(title, msg)
        self.sync_ui()

    def on_new_game(self):
        self.game.reset()
        self.selected = None
        self._last_end_kind = None

        # reset clocks (NEW)
        self.white_time = float(self.initial_time)
        self.black_time = float(self.initial_time)
        self._flag_fell = False

        self.sync_ui()

    def on_undo(self):
        self.game.undo()
        self.selected = None
        # clock undo not implemented (intentional simplicity)
        self.panel.flash_message("Undo (clock not reverted).")
        self.sync_ui()

    def on_flip(self):
        self.flipped = not self.flipped
        self.sync_ui()

    def on_hint(self):
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
            self._last_end_kind = None
            # keep clocks as-is (analysis mode); you can also reset if you prefer
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

    def tick(self, dt):
        # dt is seconds since last tick
        if self._is_game_over():
            return True

        # pause clock during promotion choice (to avoid "time-out while popup open")
        if self.game.pending_promotion is not None:
            return True

        if self.game.position.side_to_move == "w":
            self.white_time -= dt
        else:
            self.black_time -= dt

        self._check_time_flag()
        # update just the clocks/status cheaply
        self.panel.set_clocks(self.white_time, self.black_time)
        return True