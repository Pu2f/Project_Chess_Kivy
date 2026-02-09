from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup


class SidePanel(BoxLayout):
    def __init__(
        self,
        on_new_game,
        on_undo,
        on_flip,
        on_hint,
        on_toggle_highlight,
        on_load_fen,
        on_promotion_choice,
        on_claim_draw,
        on_set_clock_minutes,  # NEW
        **kwargs,
    ):
        super().__init__(
            orientation="vertical", size_hint=(0.38, 1), spacing=6, padding=6, **kwargs
        )

        self.on_promotion_choice = on_promotion_choice
        self.on_claim_draw = on_claim_draw
        self._on_new_game = on_new_game
        self.on_set_clock_minutes = on_set_clock_minutes

        self.turn_label = Label(text="Turn: -", size_hint=(1, None), height=24)
        self.status_label = Label(text="Status: -", size_hint=(1, None), height=52)
        self.msg_label = Label(text="", size_hint=(1, None), height=24)

        self.add_widget(self.turn_label)
        self.add_widget(self.status_label)
        self.add_widget(self.msg_label)

        # --- Chess clock widgets ---
        clock_row = BoxLayout(size_hint=(1, None), height=28, spacing=6)
        self.white_clock = Label(text="White: 05:00", size_hint=(0.5, 1))
        self.black_clock = Label(text="Black: 05:00", size_hint=(0.5, 1))
        clock_row.add_widget(self.white_clock)
        clock_row.add_widget(self.black_clock)
        self.add_widget(clock_row)

        # --- Clock setting (NEW) ---
        set_row = BoxLayout(size_hint=(1, None), height=32, spacing=6)
        set_row.add_widget(Label(text="Clock (min):", size_hint=(0.55, 1)))
        self.clock_minutes_input = TextInput(
            text="5",
            multiline=False,
            input_filter="int",
            size_hint=(0.45, 1),
            hint_text="e.g. 5",
        )
        # callback: press Enter to set
        self.clock_minutes_input.bind(
            on_text_validate=lambda _w: self.on_set_clock_minutes(
                self.clock_minutes_input.text
            )
        )
        set_row.add_widget(self.clock_minutes_input)
        self.add_widget(set_row)
        # ---------------------------

        # Buttons row 1
        row1 = BoxLayout(size_hint=(1, None), height=40, spacing=6)

        self.btn_new = Button(text="New", bold=True)
        self.btn_undo = Button(text="Undo")
        self.btn_flip = Button(text="Flip")
        self.btn_hint = Button(text="Hint")

        self.btn_new.bind(on_press=lambda *_: self._on_new_game())
        self.btn_undo.bind(on_press=lambda *_: on_undo())
        self.btn_flip.bind(on_press=lambda *_: on_flip())
        self.btn_hint.bind(on_press=lambda *_: on_hint())

        row1.add_widget(self.btn_new)
        row1.add_widget(self.btn_undo)
        row1.add_widget(self.btn_flip)
        row1.add_widget(self.btn_hint)
        self.add_widget(row1)

        # Buttons row 2
        row2 = BoxLayout(size_hint=(1, None), height=36, spacing=6)
        self.btn_claim = Button(text="Claim Draw")
        self.btn_claim.bind(on_press=lambda *_: self.on_claim_draw())
        row2.add_widget(self.btn_claim)
        self.add_widget(row2)

        # Highlight toggle
        hl_row = BoxLayout(size_hint=(1, None), height=30, spacing=6)
        self.hl_check = CheckBox(active=True)
        self.hl_check.bind(active=lambda _w, val: on_toggle_highlight(val))
        hl_row.add_widget(Label(text="Highlights", size_hint=(0.7, 1)))
        hl_row.add_widget(self.hl_check)
        self.add_widget(hl_row)

        # Move list
        self.moves_view = ScrollView(size_hint=(1, 1))
        self.moves_grid = GridLayout(cols=1, size_hint_y=None, spacing=2)
        self.moves_grid.bind(minimum_height=self.moves_grid.setter("height"))
        self.moves_view.add_widget(self.moves_grid)
        self.add_widget(self.moves_view)

        # FEN input
        self.fen_input = TextInput(
            text="",
            size_hint=(1, None),
            height=72,
            multiline=True,
            hint_text="Paste FEN here and press Enter (last line).",
        )
        self.fen_input.bind(
            on_text_validate=lambda _w: on_load_fen(self.fen_input.text.strip())
        )
        self.add_widget(self.fen_input)

        self._promotion_popup = None

    def set_turn(self, txt):
        self.turn_label.text = f"Turn: {txt}"

    def set_status(self, txt):
        self.status_label.text = f"Status: {txt}"

    def set_moves(self, moves):
        self.moves_grid.clear_widgets()
        for i, m in enumerate(moves, start=1):
            self.moves_grid.add_widget(
                Label(text=f"{i}. {m}", size_hint_y=None, height=20)
            )

    def set_fen(self, fen):
        self.fen_input.text = fen

    def flash_message(self, msg):
        self.msg_label.text = msg if msg else "..."

    def open_info_popup(self, title: str, message: str):
        box = BoxLayout(orientation="vertical", spacing=8, padding=8)
        box.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint=(1, None), height=38)
        popup = Popup(title=title, content=box, size_hint=(0.75, 0.35))
        btn.bind(on_press=lambda *_: popup.dismiss())
        box.add_widget(btn)
        popup.open()

    def set_game_over_mode(self, game_over: bool):
        self.btn_undo.disabled = game_over
        self.btn_hint.disabled = game_over
        self.btn_claim.disabled = game_over

        if game_over:
            self.btn_new.text = "NEW GAME"
            self.btn_new.font_size = 20
        else:
            self.btn_new.text = "New"
            self.btn_new.font_size = 14

    def set_clocks(self, white_seconds: float, black_seconds: float):
        def fmt(sec: float) -> str:
            sec = max(0, int(sec))
            m = sec // 60
            s = sec % 60
            return f"{m:02d}:{s:02d}"

        self.white_clock.text = f"White: {fmt(white_seconds)}"
        self.black_clock.text = f"Black: {fmt(black_seconds)}"

    def open_promotion_dialog(self, _side_to_move):
        pieces = ["Q", "R", "B", "N"]
        box = BoxLayout(orientation="vertical", spacing=6, padding=6)
        box.add_widget(Label(text="Promotion! Choose wisely (no pressure)."))

        row = BoxLayout(size_hint=(1, None), height=40, spacing=6)
        for p in pieces:
            b = Button(text=p)
            b.bind(on_press=lambda _w, pp=p: self._choose_promotion(pp))
            row.add_widget(b)
        box.add_widget(row)

        self._promotion_popup = Popup(
            title="Promotion", content=box, size_hint=(0.6, 0.3)
        )
        self._promotion_popup.open()

    def _choose_promotion(self, piece_letter):
        if self._promotion_popup:
            self._promotion_popup.dismiss()
            self._promotion_popup = None
        self.on_promotion_choice(piece_letter)
