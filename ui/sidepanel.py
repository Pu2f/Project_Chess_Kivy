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
        **kwargs
    ):
        super().__init__(orientation="vertical", size_hint=(0.38, 1), spacing=6, padding=6, **kwargs)

        self.turn_label = Label(text="Turn: -", size_hint=(1, None), height=24)
        self.status_label = Label(text="Status: -", size_hint=(1, None), height=48)
        self.msg_label = Label(text="", size_hint=(1, None), height=24)

        self.add_widget(self.turn_label)
        self.add_widget(self.status_label)
        self.add_widget(self.msg_label)

        # Buttons row
        row = BoxLayout(size_hint=(1, None), height=36, spacing=6)
        btn_new = Button(text="New")
        btn_undo = Button(text="Undo")
        btn_flip = Button(text="Flip")
        btn_hint = Button(text="Hint")

        btn_new.bind(on_press=lambda *_: on_new_game())  # callback #3
        btn_undo.bind(on_press=lambda *_: on_undo())     # callback #4
        btn_flip.bind(on_press=lambda *_: on_flip())     # callback #5
        btn_hint.bind(on_press=lambda *_: on_hint())     # callback #6

        row.add_widget(btn_new)
        row.add_widget(btn_undo)
        row.add_widget(btn_flip)
        row.add_widget(btn_hint)
        self.add_widget(row)

        # Highlight toggle
        hl_row = BoxLayout(size_hint=(1, None), height=30, spacing=6)
        self.hl_check = CheckBox(active=True)
        self.hl_check.bind(active=lambda _w, val: on_toggle_highlight(val))  # callback #7
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
        self.fen_input.bind(on_text_validate=lambda _w: on_load_fen(self.fen_input.text.strip()))  # callback #8
        self.add_widget(self.fen_input)

        self._promotion_popup = None
        self._pending_promotion = None

    def set_turn(self, txt):
        self.turn_label.text = f"Turn: {txt}"

    def set_status(self, txt):
        self.status_label.text = f"Status: {txt}"

    def set_moves(self, moves):
        self.moves_grid.clear_widgets()
        for i, m in enumerate(moves, start=1):
            self.moves_grid.add_widget(Label(text=f"{i}. {m}", size_hint_y=None, height=20))

    def set_fen(self, fen):
        self.fen_input.text = fen

    def flash_message(self, msg):
        # humor แบบพอดี: สั้น แสบ นิด
        self.msg_label.text = msg if msg else "..."

    def open_promotion_dialog(self, side_to_move):
        # สำหรับความครบ: เลือกโปรโมตเป็น Q/R/B/N
        pieces = ["Q", "R", "B", "N"]
        box = BoxLayout(orientation="vertical", spacing=6, padding=6)
        box.add_widget(Label(text="Promotion! Choose wisely (like your life depends on it)."))

        row = BoxLayout(size_hint=(1, None), height=40, spacing=6)
        for p in pieces:
            b = Button(text=p)
            b.bind(on_press=lambda _w, pp=p: self._choose_promotion(pp))  # callback #9
            row.add_widget(b)
        box.add_widget(row)

        self._promotion_popup = Popup(title="Promotion", content=box, size_hint=(0.6, 0.3))
        self._promotion_popup.open()

    def _choose_promotion(self, piece_letter):
        # Root จะไปอ่าน game.pending_promotion
        # ที่นี่แค่ปิด popup; ตัว engine จะให้ UI เรียก game.promote(...)
        if self._promotion_popup:
            self._promotion_popup.dismiss()
            self._promotion_popup = None
        # ส่งผ่าน “ช่องข้อความ” เพื่อให้ผู้ใช้รู้ว่าต้องคลิกเดินอีกไหม
        self.flash_message(f"Promote to {piece_letter} (engine will apply).")