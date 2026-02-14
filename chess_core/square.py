#   A classe Square representa o quadrado no tabuleiro e armazena uma peça. Caso não tenha nenhuma
#peça no quadrado, Square amazena um EmptySquare

class EmptySquare:

    def __init__(self) -> None:
        self.iswhite = None
        self.moved = None
        self.value = 0
        self.image = "images/Clear.png"
        self.selected = False
        self.selected_image = "images/selected-clear.png"

    def __str__(self) -> str:
        return '.'
    
    def possible_move(self, start, end):
        return False
    
    def get_selected_image(self):
        if self.selected:
            return self.selected_image
        return self.image


class Square:

    def __init__(self, x, y, piece = None) -> None:

        self.x = x
        self.y = y
        if piece is None:
            self.piece = EmptySquare()
        else:
            self.piece = piece
        
    def __repr__(self) -> str:
        if self.piece == None:
            return '.'
        return self.piece.__str__()