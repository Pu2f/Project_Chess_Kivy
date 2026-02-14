from chess_core.square import Square

#   Cada peça é uma classe, contendo atributos como iswhite, que determina se a peça é branca ou preta,
# selected, que serve para mudar a imagem caso a imagem seja selecionada, e o caminho para a imagens
# de cada peça.


class Piece:

    def __init__(self, iswhite) -> None:

        self.iswhite = iswhite
        self.moved = False
        self.value = 0
        self.selected = False

    def get_selected_image(self):
        if self.selected:
            return self.selected_image
        return self.image


class Pawn(Piece):

    def __init__(self, iswhite) -> None:
        super().__init__(iswhite)

        # Set value of the piece
        if self.iswhite:
            self.image = "images/white-pawn.png"
            self.selected_image = "images/selected-white-pawn.png"
            self.value = 1
        else:
            self.image = "images/black-pawn.png"
            self.selected_image = "images/selected-black-pawn.png"
            self.value = -1
        self.en_passantable = False

    def __str__(self) -> str:
        if self.iswhite:
            return "P"
        return "p"

    def possible_move(self, start: Square, end: Square):

        # Can't move if the square is ocupied
        if end.piece.iswhite == self.iswhite:
            return False

        if start.y != end.y:
            return False

        # Can only move in one direction
        if not self.iswhite:
            if start.x - end.x == 1:
                return True
            # The first move can be two squares
            if start.x - end.x == 2 and not self.moved:
                return True
        else:
            if end.x - start.x == 1:
                return True
            # The first move can be two squares
            if end.x - start.x == 2 and not self.moved:
                return True
        return False


class Bishop(Piece):

    def __init__(self, iswhite) -> None:
        super().__init__(iswhite)

        if self.iswhite:
            self.image = "images/white-bishop.png"
            self.selected_image = "images/selected-white-bishop.png"
            self.value = 3
        else:
            self.image = "images/black-bishop.png"
            self.selected_image = "images/selected-black-bishop.png"
            self.value = -3

    def __str__(self) -> str:
        if self.iswhite:
            return "B"
        return "b"

    def possible_move(self, start: Square, end: Square):

        # Can't move if the square is ocupied
        if end.piece.iswhite == self.iswhite:
            return False

        x = abs(start.x - end.x)
        y = abs(start.y - end.y)

        # Can only move on diagonal
        if x == y:
            return True
        return False


class Knight(Piece):

    def __init__(self, iswhite) -> None:
        super().__init__(iswhite)

        # Set value of the piece
        if self.iswhite:
            self.image = "images/white-knight.png"
            self.selected_image = "images/selected-white-knight.png"
            self.value = 3
        else:
            self.image = "images/black-knight.png"
            self.selected_image = "images/selected-black-knight.png"
            self.value = -3

    def __str__(self) -> str:
        if self.iswhite:
            return "N"
        return "n"

    def possible_move(self, start: Square, end: Square):

        # Can't move if the square is ocupied
        if end.piece.iswhite == self.iswhite:
            return False

        x = abs(start.x - end.x)
        y = abs(start.y - end.y)

        # Can only move in a L
        if (x == 2 and y == 1) or (y == 2 and x == 1):
            return True
        return False


class Rook(Piece):

    def __init__(self, iswhite) -> None:
        super().__init__(iswhite)

        # Set value of the piece
        if self.iswhite:
            self.image = "images/white-rook.png"
            self.selected_image = "images/selected-white-rook.png"
            self.value = 5
        else:
            self.image = "images/black-rook.png"
            self.selected_image = "images/selected-black-rook.png"
            self.value = -5

    def __str__(self) -> str:

        if self.iswhite:
            return "R"
        return "r"

    def possible_move(self, start: Square, end: Square):

        # Can't move if the square is ocupied
        if end.piece.iswhite == self.iswhite:
            return False

        x = abs(start.x - end.x)
        y = abs(start.y - end.y)

        # Can only move in the same line or column
        if x == 0 or y == 0:
            return True
        return False


class Queen(Piece):

    def __init__(self, iswhite) -> None:
        super().__init__(iswhite)

        # Set value of the piece
        if self.iswhite:
            self.image = "images/white-queen.png"
            self.selected_image = "images/selected-white-queen.png"
            self.value = 9
        else:
            self.image = "images/black-queen.png"
            self.selected_image = "images/selected-black-queen.png"
            self.value = -9

    def __str__(self) -> str:

        if self.iswhite:
            return "Q"
        return "q"

    def possible_move(self, start: Square, end: Square):

        # Can't move if the square is ocupied
        if end.piece.iswhite == self.iswhite:
            return False

        x = abs(start.x - end.x)
        y = abs(start.y - end.y)

        # Basically, rook and bishop combined
        if x == y:
            return True
        if x == 0 or y == 0:
            return True
        return False


class King(Piece):

    def __init__(self, iswhite) -> None:
        super().__init__(iswhite)

        # Set value of the piece
        if self.iswhite:
            self.image = "images/white-king.png"
            self.selected_image = "images/selected-white-king.png"
            self.value = 100
        else:
            self.image = "images/black-king.png"
            self.selected_image = "images/selected-black-king.png"
            self.value = -100

    def __str__(self) -> str:

        if self.iswhite:
            return "K"
        return "k"

    def possible_move(self, start: Square, end: Square):

        # Can't move if the square is ocupied
        if end.piece.iswhite == self.iswhite:
            return False

        # Check for regular movement
        x = abs(end.x - start.x)
        y = abs(end.y - start.y)

        if (x == 1 or y == 1) and (not (x > 1 or y > 1)):
            return True
        return False
