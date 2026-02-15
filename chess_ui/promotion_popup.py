from __future__ import annotations

from typing import Callable

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


class PromotionPopup(Popup):
    """
    Pawn promotion picker.
    Calls on_pick with one of: 'q', 'r', 'b', 'n'
    """

    def __init__(self, on_pick: Callable[[str], None], **kwargs):
        super().__init__(**kwargs)
        self.title = "Promotion"
        self.size_hint = (None, None)
        self.size = (360, 180)
        self.auto_dismiss = False

        root = BoxLayout(orientation="vertical", padding=10, spacing=10)
        root.add_widget(Label(text="Choose a piece to promote to (Q/R/B/N)", size_hint_y=None, height=30))

        row = BoxLayout(orientation="horizontal", spacing=10)

        def add_btn(text: str, code: str):
            btn = Button(text=text)
            btn.bind(on_release=lambda _btn: self._pick(on_pick, code))
            row.add_widget(btn)

        add_btn("Queen (Q)", "q")
        add_btn("Rook (R)", "r")
        add_btn("Bishop (B)", "b")
        add_btn("Knight (N)", "n")

        root.add_widget(row)
        self.content = root

    def _pick(self, on_pick: Callable[[str], None], code: str) -> None:
        self.dismiss()
        on_pick(code)