from chess_core.board import Board
from chess_core.rules import turn

class GameController:
    """
    Controller to manage game state and coordinate conversions between UI and model.
    Handles: selected state, turn tracking, view flipping, and UI<->model coordinate conversion.
    """
    
    def __init__(self):
        self.selected = False
        self.s_x = None  # Selected piece x coordinate (in model space)
        self.s_y = None  # Selected piece y coordinate (in model space)
        self.turn_white = True  # Whose turn it is
        self.white_view = True  # Which side is viewing from bottom
        
    def ui_to_model(self, ui_x, ui_y):
        """Convert UI coordinates to model coordinates based on current view"""
        if self.white_view:
            return ui_x, ui_y
        return 7 - ui_x, 7 - ui_y
    
    def model_to_ui(self, model_x, model_y):
        """Convert model coordinates to UI coordinates based on current view"""
        if self.white_view:
            return model_x, model_y
        return 7 - model_x, 7 - model_y
    
    def reset(self):
        """Reset the game state"""
        Board.create_board()
        self.selected = False
        self.s_x = None
        self.s_y = None
        self.turn_white = True
        self.white_view = True
    
    def select_piece(self, model_x, model_y):
        """Select a piece at the given model coordinates"""
        self.selected = True
        self.s_x = model_x
        self.s_y = model_y
        Board.board[model_x][model_y].piece.selected = True
    
    def deselect_piece(self):
        """Deselect the currently selected piece"""
        if self.selected and self.s_x is not None and self.s_y is not None:
            Board.board[self.s_x][self.s_y].piece.selected = False
        self.selected = False
    
    def attempt_move(self, from_x, from_y, to_x, to_y):
        """
        Attempt to move a piece from (from_x, from_y) to (to_x, to_y) in model coordinates.
        Returns True if the move was successful, False otherwise.
        """
        success = turn(from_x, from_y, to_x, to_y, self.turn_white)
        if success:
            # Flip view and change turn on successful move
            self.turn_white = not self.turn_white
            self.white_view = not self.white_view
        return success
    
    def handle_click(self, ui_x, ui_y):
        """
        Handle a click at UI coordinates (ui_x, ui_y).
        Returns True if the board should be re-rendered.
        """
        # Convert UI coordinates to model coordinates
        model_x, model_y = self.ui_to_model(ui_x, ui_y)
        
        if not self.selected:
            # First click: select piece
            self.select_piece(model_x, model_y)
            return True
        else:
            # Second click: attempt move
            success = self.attempt_move(self.s_x, self.s_y, model_x, model_y)
            
            # Deselect both pieces regardless of success
            self.deselect_piece()
            Board.board[model_x][model_y].piece.selected = False
            
            return True
    
    def get_turn_icon(self):
        """Get the icon path for the current turn"""
        if self.turn_white:
            return "images/white-king.png"
        else:
            return "images/black-king.png"
