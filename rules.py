from pieces import *
from square import *
from board import *

#   Neste módulo, temos regras do jogo em si, como checks, checkmates, promoções e os turnos.
#   Com algumas pequenas modificações, é possível jogar o jogo neste módulo, através do terminal.

def check_for_check(iswhite : bool) -> bool:

    #find the king
    for line in Board.board:
        for square in line:
            if isinstance(square.piece, King) and square.piece.iswhite == iswhite:
                king_square = square

    #check if any piece has a path to the king
    for line in Board.board:
        for square in line:
            if square.piece.iswhite == king_square.piece.iswhite or isinstance(square.piece, EmptySquare):
                continue
            if isinstance(square.piece, Rook):
                if has_path_rook(square, king_square):
                    return True
            elif isinstance(square.piece, Bishop):
                if has_path_bishop(square, king_square):
                    return True
            elif isinstance(square.piece, Queen):
                if has_path_bishop(square, king_square) or has_path_rook(square, king_square):
                    return True
            elif isinstance(square.piece, King):
                if square.piece.possible_move(square, king_square):
                    return True
            elif isinstance(square.piece, Knight):
                if square.piece.possible_move(square, king_square):
                    return True
            elif isinstance(square.piece, Pawn):
                if pawn_can_capture(square, king_square):
                    return True
    return False


def end_turn(iswhite : bool) -> None:

    for line in Board.board:
        for square in line:
            if square.piece.iswhite != iswhite and isinstance(square.piece, Pawn):
                square.piece.en_passantable = False

    #Check for promotions
    if iswhite:
        line = 7
    else:
        line = 0

    for square in Board.board[line]:
        if isinstance(square.piece, Pawn):
            square.piece = Queen(iswhite)

#checks for all possible moves
def check_for_checkmate(iswhite):

    for a in range(8):
        for b in range(8):
            if isinstance(Board.board[a][b].piece, EmptySquare):
                        continue
            if Board.board[a][b].piece.iswhite != iswhite:
                        continue

            for c in range(8):
                for d in range(8):
                    if a == c and b == d:
                        continue

                    start_piece = Board.board[a][b].piece
                    end_piece = Board.board[c][d].piece

                    if turn(a, b, c, d, iswhite, True): #If turn is possible, it's not mate

                        Board.board[c][d].piece = end_piece
                        Board.board[a][b].piece = start_piece
                        return False
                    
                    #Garantees that pieces en_passantable is correct
                    Board.board[a][b].piece.en_passantable = False
    return True


def turn(x1 ,y1, x2, y2, iswhite, check = False):

    start : Square = Board.board[x1][y1]
    end : Square = Board.board[x2][y2]

    #select the pieces to reverse movement if check
    s_piece = start.piece
    e_piece = end.piece

    #save piece movement property
    s_moved = s_piece.moved
    e_moved = e_piece.moved

    if start.piece.iswhite == iswhite:
        if move_piece(start, end):

            #if move creates check in it's own king, it's ilegal
            if check_for_check(iswhite):
                #reverses the movement
                Board.board[start.x][start.y].piece = s_piece
                Board.board[end.x][end.y].piece = e_piece
                Board.board[start.x][start.y].piece.moved = s_moved
                Board.board[end.x][end.y].piece.moved = e_moved
                return False
            
            #promotions and reset en_passantable
            end_turn(iswhite)
            
            #check for checkmate on enemy king
            other_iswhite = not iswhite
            if check_for_check(other_iswhite):
                if check_for_checkmate(other_iswhite):
                    
                    #if checkmate, mated king becomes red
                    for i in range(64):
                        if (isinstance(Board.board[i//8][i%8].piece, King) and 
                            Board.board[i//8][i%8].piece.iswhite == other_iswhite):

                            Board.board[i//8][i%8].piece.selected = True
            return True
    return False


def main():
    Board.create_board()
    Board.print_board()

if __name__ == "__main__":
    main()