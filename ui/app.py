from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock

from ui.root import ChessRoot


class ChessApp(App):
    def build(self):
        self.title = "Kivy Chess (Unicode)"
        root = ChessRoot()
        Window.bind(on_key_down=root.on_key_down)  # callback #10
        Clock.schedule_interval(root.tick, 0.2)    # callback #11 (optional clock)
        return root