from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
import os

from chess_core.board import Board
from game.controller import GameController
from app.widgets import BoardGrid, Sidebar


class ChessGame(BoxLayout):
    """Main game widget containing board and sidebar"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize game
        Board.create_board()
        self.controller = GameController()
        
        # Create board grid
        self.board_grid = BoardGrid(self.controller)
        self.add_widget(self.board_grid)
        
        # Create sidebar
        self.sidebar = Sidebar(self.controller, self.board_grid)
        self.add_widget(self.sidebar)
        
        # Connect board to sidebar
        self.board_grid.sidebar = self.sidebar
        
        # Initial render
        self.board_grid.render()


class ChessApp(App):
    """Main Kivy application"""
    
    def build(self):
        # Load KV file
        kv_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'chess.kv')
        Builder.load_file(kv_path)
        return ChessGame()
