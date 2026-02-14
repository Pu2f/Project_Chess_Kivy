from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

from chess_core.board import Board
from game.controller import GameController


class TileButton(Button):
    """A single tile button on the chess board"""
    
    def __init__(self, x, y, board_grid, **kwargs):
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.board_grid = board_grid
        self.background_color = (1, 1, 1, 0)  # Transparent background
        

class BoardGrid(GridLayout):
    """
    The chess board grid that displays pieces and handles clicks.
    Creates an 8x8 grid of buttons dynamically without using 64 StringProperties.
    """
    
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.sidebar = None  # Will be set by ChessGame
        self.cols = 8
        self.buttons = []  # Store button references
        
        # Calculate board size
        w, h = Window.size
        self.board_size = min(w, h)
        self.row_force_default = True
        self.col_force_default = True
        self.row_default_height = self.board_size / 8
        self.col_default_width = self.board_size / 8
        
        # Create 8x8 grid of buttons
        # Create from top to bottom (7 to 0) for visual layout
        for row in range(7, -1, -1):
            for col in range(8):
                btn = TileButton(row, col, self)
                btn.bind(on_press=self._on_button_press)
                self.buttons.append(btn)
                self.add_widget(btn)
        
        # Set the board background
        with self.canvas.before:
            self.bg_rect = Rectangle(size=(self.board_size, self.board_size), 
                                     source="images/Board.png")
        self.bind(size=self._update_bg, pos=self._update_bg)
    
    def _update_bg(self, *args):
        """Update background rectangle"""
        self.bg_rect.size = (self.board_size, self.board_size)
    
    def _on_button_press(self, btn):
        """Handle button press event"""
        self.on_tile_click(btn.x, btn.y)
    
    def on_tile_click(self, x, y):
        """Handle a tile click"""
        should_render = self.controller.handle_click(x, y)
        if should_render:
            self.render()
            if self.sidebar:
                self.sidebar.update_turn_icon()
    
    def render(self):
        """Render all pieces on the board based on current game state"""
        # Update all button images based on model state
        for btn in self.buttons:
            ui_x, ui_y = btn.x, btn.y
            model_x, model_y = self.controller.ui_to_model(ui_x, ui_y)
            piece = Board.board[model_x][model_y].piece
            btn.background_normal = piece.get_selected_image()


class Sidebar(BoxLayout):
    """Sidebar UI with turn indicator and restart button"""
    
    def __init__(self, controller, board_grid, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.board_grid = board_grid
        self.orientation = 'vertical'
        
        w, h = Window.size
        ui_size_x = max(w, h) - min(w, h)
        ui_size_y = min(w, h)
        
        self.size_hint = (None, None)
        self.size = (ui_size_x, ui_size_y)
        
        # Turn indicator image
        self.turn_image = Image(source=self.controller.get_turn_icon(),
                               allow_stretch=True,
                               size_hint=(None, None),
                               size=(ui_size_x, ui_size_x))
        self.add_widget(self.turn_image)
        
        # Restart button
        restart_btn = Button(text='Restart',
                            size_hint=(None, None),
                            size=(ui_size_x, 60),
                            pos_hint={'center_x': 0.5})
        restart_btn.bind(on_press=self.on_restart)
        self.add_widget(restart_btn)
        
        # Background
        with self.canvas.before:
            Color(0.7, 0.7, 0.7, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg, pos=self._update_bg)
    
    def _update_bg(self, *args):
        """Update background rectangle"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def on_restart(self, instance):
        """Handle restart button click"""
        self.controller.reset()
        self.board_grid.render()
        self.update_turn_icon()
    
    def update_turn_icon(self):
        """Update the turn indicator icon"""
        self.turn_image.source = self.controller.get_turn_icon()
