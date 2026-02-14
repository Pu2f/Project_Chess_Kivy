# Module for tracking chess move history
# Stores each move made during the game with complete information

class Move:
    """Represents a single chess move with all relevant information"""
    
    def __init__(self, from_x, from_y, to_x, to_y, piece_type, piece_color, captured_piece=None, special_move=None):
        """
        Initialize a move record
        
        Args:
            from_x: Starting x coordinate
            from_y: Starting y coordinate
            to_x: Ending x coordinate
            to_y: Ending y coordinate
            piece_type: Type of piece moved (e.g., 'Pawn', 'Knight')
            piece_color: Color of piece ('white' or 'black')
            captured_piece: Type of captured piece, if any
            special_move: Special move type ('castling', 'en_passant', 'promotion', etc.)
        """
        self.from_x = from_x
        self.from_y = from_y
        self.to_x = to_x
        self.to_y = to_y
        self.piece_type = piece_type
        self.piece_color = piece_color
        self.captured_piece = captured_piece
        self.special_move = special_move
        
    def to_algebraic(self):
        """Convert move to algebraic notation (e.g., 'e2e4')"""
        files = 'abcdefgh'
        ranks = '12345678'
        from_square = files[self.from_y] + ranks[self.from_x]
        to_square = files[self.to_y] + ranks[self.to_x]
        return from_square + to_square
    
    def __str__(self):
        """Return a human-readable string representation of the move"""
        color = "White" if self.piece_color == "white" else "Black"
        move_str = f"{color} {self.piece_type}: {self.to_algebraic()}"
        
        if self.captured_piece:
            move_str += f" (captured {self.captured_piece})"
        if self.special_move:
            move_str += f" [{self.special_move}]"
            
        return move_str


class MoveHistory:
    """Manages the history of all moves in a chess game"""
    
    def __init__(self):
        """Initialize an empty move history"""
        self.moves = []
        
    def add_move(self, move):
        """
        Add a move to the history
        
        Args:
            move: Move object to add
        """
        self.moves.append(move)
        
    def get_all_moves(self):
        """Return list of all moves"""
        return self.moves
    
    def get_move_count(self):
        """Return the total number of moves"""
        return len(self.moves)
    
    def get_last_move(self):
        """Return the last move made, or None if no moves"""
        if self.moves:
            return self.moves[-1]
        return None
    
    def clear(self):
        """Clear all move history"""
        self.moves = []
    
    def to_list(self):
        """Return move history as a list of strings"""
        return [str(move) for move in self.moves]
    
    def to_algebraic_list(self):
        """Return move history as a list of algebraic notation strings"""
        return [move.to_algebraic() for move in self.moves]
    
    def __str__(self):
        """Return a formatted string of all moves"""
        if not self.moves:
            return "No moves yet"
        
        result = "Move History:\n"
        for i, move in enumerate(self.moves, 1):
            result += f"{i}. {move}\n"
        return result
