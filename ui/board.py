from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ListProperty
from kivy.metrics import dp

from engine.pieces import piece_to_unicode


class SquareButton(Button):
    file = NumericProperty(0)  # 0..7
    rank = NumericProperty(0)  # 0..7
    base_color = ListProperty([1, 1, 1, 1])

    def __init__(self, on_square, **kwargs):
        super().__init__(**kwargs)
        # ใน SquareButton.__init__
        self.font_name = "assets/fonts/NotoSansSymbols2-Regular.ttf"
        self.on_square = on_square
        self.font_size = dp(26)
        self.markup = True

        self.bind(on_press=self._on_press)  # callback #1
        self.bind(on_release=self._on_release)  # callback #2

    def sq(self):
        return self.rank * 8 + self.file  # 0=a1 ... 63=h8 (เราจะนิยาม a1 = 0)

    def _on_press(self, *_args):
        self.on_square(self.sq())

    def _on_release(self, *_args):
        # กัน event ซ้ำ ๆ (ปล่อยไว้เป็น hook)
        pass


class BoardGrid(GridLayout):
    def __init__(self, on_square, **kwargs):
        super().__init__(cols=8, spacing=1, padding=1, **kwargs)
        self.on_square = on_square
        self.squares = []
        self.flipped = False
        self.highlight_from = None
        self.highlight_tos = set()

        for ui_rank in range(7, -1, -1):
            for ui_file in range(8):
                btn = SquareButton(on_square=self.on_square)
                btn.file = ui_file
                btn.rank = ui_rank
                self.squares.append(btn)
                self.add_widget(btn)

        self.bind(size=self._on_size)  # callback #9 (resize)

    def _on_size(self, *_args):
        # ทำช่องให้เป็นสี่เหลี่ยม
        cell = min(self.width, self.height) / 8.0
        for b in self.squares:
            b.size_hint = (None, None)
            b.size = (cell, cell)

    def set_highlights(self, from_sq, to_sqs):
        self.highlight_from = from_sq
        self.highlight_tos = set(to_sqs)

    def clear_highlights(self):
        self.highlight_from = None
        self.highlight_tos = set()

    def set_position(self, position, flipped=False):
        self.flipped = flipped

        # map UI square index -> engine square index
        def ui_sq_to_engine_sq(ui_sq):
            # ui_sq is based on btn.rank/file where rank 0=a1
            if not flipped:
                return ui_sq
            # flip: a1 <-> h8
            return 63 - ui_sq

        for btn in self.squares:
            ui_sq = btn.sq()
            sq = ui_sq_to_engine_sq(ui_sq)

            piece = position.board[sq]
            btn.text = piece_to_unicode(piece)

            light = (btn.file + btn.rank) % 2 == 0
            base = [0.93, 0.92, 0.88, 1] if light else [0.35, 0.45, 0.35, 1]

            # highlight
            if self.highlight_from == sq:
                base = [0.95, 0.75, 0.2, 1]
            elif sq in self.highlight_tos:
                base = [0.7, 0.85, 0.3, 1]

            btn.background_color = base
