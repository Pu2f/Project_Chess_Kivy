from chess_core.board import Board
from chess_core.rules import turn
from chess_core.pieces import *
from chess_core.square import Square


class Game:

    def __init__(self):
        self.waiting_promotion = None
        self.board = Board()
        self.current_turn = True
        self.move_history = []

    def move(self, x1, y1, x2, y2):

        result = turn(self.board, x1, y1, x2, y2, self.current_turn)

        if result is False:
            return False

        self.move_history.append((x1, y1, x2, y2))

        if isinstance(result, Square):
            self.waiting_promotion = result
            return True

        self.current_turn = not self.current_turn
        return True

    def promote(self, piece_type):

        if not isinstance(self.waiting_promotion, Square):
            return

        square = self.waiting_promotion
        iswhite = square.piece.iswhite

        if piece_type == "queen":
            square.piece = Queen(iswhite)
        elif piece_type == "rook":
            square.piece = Rook(iswhite)
        elif piece_type == "bishop":
            square.piece = Bishop(iswhite)
        elif piece_type == "knight":
            square.piece = Knight(iswhite)

        self.waiting_promotion = None
        self.current_turn = not self.current_turn
