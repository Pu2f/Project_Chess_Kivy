from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple, Optional

from kivy.uix.label import Label


def _project_root() -> Path:
    # chess_ui/font_piece_renderer.py -> project root
    return Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class PieceFontTheme:
    # ใช้ path แบบ absolute กันพลาด working directory
    font_path: str = str(_project_root() / "assets" / "ChessCases.ttf")
    back_color: Tuple[float, float, float, float] = (1, 1, 1, 1)
    front_color: Tuple[float, float, float, float] = (0, 0, 0, 1)


class ChessCasesRenderer:
    _BACKGROUND_TEXTURES = {
        "K": "k", "Q": "l", "R": "m", "B": "n", "N": "o", "P": "p",
        "k": "q", "q": "r", "r": "s", "b": "t", "n": "u", "p": "v",
    }
    _FRONT_TEXTURES = {
        "K": "H", "Q": "I", "R": "J", "B": "K", "N": "L", "P": "M",
        "k": "N", "q": "O", "r": "P", "b": "Q", "n": "R", "p": "S",
    }
    _GLYPHS = "klmnopqrstuvHIJKLMNOPQRS"

    def __init__(self, theme: PieceFontTheme = PieceFontTheme()):
        self._theme = theme
        self._font_size: Optional[int] = None
        self._textures: Dict[str, Label] = {}

    def ensure_cache(self, square_size: int) -> None:
        if self._font_size == square_size and self._textures:
            return
        self._font_size = square_size
        self._textures = {}
        for ch in self._GLYPHS:
            lbl = Label(text=ch, font_name=self._theme.font_path, font_size=square_size)
            lbl.texture_update()
            self._textures[ch] = lbl

    def get_layers(self, piece_letter: str) -> Optional[tuple[Label, Label]]:
        if not piece_letter or piece_letter == ".":
            return None
        bg_key = self._BACKGROUND_TEXTURES.get(piece_letter)
        fr_key = self._FRONT_TEXTURES.get(piece_letter)
        if not bg_key or not fr_key:
            return None
        return self._textures[bg_key], self._textures[fr_key]

    @property
    def colors(self):
        return self._theme.back_color, self._theme.front_color