from __future__ import annotations

from typing import Callable, Tuple

from kivy.graphics import Color, Rectangle, Line
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget

from chess_ui.font_piece_renderer import ChessCasesRenderer


class SquareWidget(ButtonBehavior, Widget):
    """
    ช่อง 1 ช่อง (โปร่งใส) วาดเฉพาะ:
    - highlight เมื่อ selected
    - legal move hints (จุด/กรอบ)
    - ตัวหมากแบบ 2-layer จาก ChessCasesRenderer บน canvas.after
    """

    def __init__(
        self,
        ui_x: int,
        ui_y: int,
        ui_to_model: Callable[[int, int], Tuple[int, int]],
        on_click_model: Callable[[int, int], None],
        board_getter: Callable[[], object],
        piece_letter_getter: Callable[[object], str],
        renderer: ChessCasesRenderer,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.ui_x = ui_x
        self.ui_y = ui_y
        self._ui_to_model = ui_to_model
        self._on_click_model = on_click_model
        self._board_getter = board_getter
        self._piece_letter_getter = piece_letter_getter
        self._renderer = renderer

        with self.canvas:
            # selected highlight (เขียว)
            self._hl_color = Color(0, 0, 0, 0)
            self._hl_line = Line(rectangle=(*self.pos, *self.size), width=2.0)

        self.bind(pos=self._redraw, size=self._redraw)

    def on_press(self) -> None:
        mx, my = self._ui_to_model(self.ui_x, self.ui_y)
        self._on_click_model(mx, my)

    def _redraw(self, *_args) -> None:
        self._hl_line.rectangle = (*self.pos, *self.size)

        mx, my = self._ui_to_model(self.ui_x, self.ui_y)
        sq = self._board_getter()[mx][my]
        piece = sq.piece

        # highlight selected จาก flag เดิมในโปรเจกต์คุณ
        is_selected = bool(getattr(piece, "selected", False))
        self._hl_color.rgba = (0.2, 0.85, 0.2, 0.9) if is_selected else (0, 0, 0, 0)

        # วาดตัวหมาก + hints บน canvas.after
        self.canvas.after.clear()

        # ---- NEW: legal move hints ----
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        radius = min(self.width, self.height) * 0.18

        with self.canvas.after:
            # capture = กรอบแดงบาง
            if bool(getattr(sq, "legal_capture", False)):
                Color(0.9, 0.1, 0.1, 0.9)
                Line(rectangle=(self.x + 3, self.y + 3, self.width - 6, self.height - 6), width=1.6)

            # move = จุดฟ้าอ่อน
            if bool(getattr(sq, "legal_move", False)):
                Color(0.2, 0.6, 1.0, 0.65)
                Line(circle=(cx, cy, radius), width=2.0)

            # castle = จุดม่วง
            if bool(getattr(sq, "legal_castle", False)):
                Color(0.6, 0.2, 0.9, 0.75)
                Line(circle=(cx, cy, radius * 1.05), width=2.2)

        # ---- draw pieces ----
        piece_letter = self._piece_letter_getter(piece)
        layers = self._renderer.get_layers(piece_letter)
        if not layers:
            return

        bg_lbl, fr_lbl = layers
        back_color, front_color = self._renderer.colors

        def centered_pos(tex_size):
            tw, th = tex_size
            return (self.x + (self.width - tw) / 2, self.y + (self.height - th) / 2)

        with self.canvas.after:
            Color(*back_color)
            Rectangle(texture=bg_lbl.texture, pos=centered_pos(bg_lbl.texture_size), size=bg_lbl.texture_size)
            Color(*front_color)
            Rectangle(texture=fr_lbl.texture, pos=centered_pos(fr_lbl.texture_size), size=fr_lbl.texture_size)

    def refresh(self) -> None:
        self._redraw()