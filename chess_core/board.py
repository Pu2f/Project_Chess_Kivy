from chess_core.square import *
from chess_core.pieces import *

def board_range(num): #used to verify movements of most pieces

    if num == 0:
        return []
    if num >= 1:
        return range(1, num)
    if num <= -1:
        return range(-1, num, -1)

#O tabuleiro em si. Temos o método create_board(), que preenche o tabuleiro com peças
#   Nesta classe o movimento de cada peça é verificado e em métodos como has_path_rook e can_castle,
#além de realizar o movimento propriamente dito

class Board:

    board = []

    def create_board():

        line = [Square(0, 0 ,Rook(True)),
                Square(0, 1 ,Knight(True)),
                Square(0, 2 ,Bishop(True)),
                Square(0, 3 ,Queen(True)),
                Square(0, 4 ,King(True)),
                Square(0, 5 ,Bishop(True)),
                Square(0, 6 ,Knight(True)),
                Square(0, 7 ,Rook(True))]
        Board.board.append(line)

        line = []
        for i in range(8):
            line.append(Square(1, i, Pawn(True)))
        Board.board.append(line)

        for i in range(2, 6):
            line = []
            for j in range(8):
                line.append(Square(i, j))

            Board.board.append(line)

        line = []
        for i in range(8):
            line.append(Square(6, i, Pawn(False)))
        Board.board.append(line)

        line = [Square(7, 0 ,Rook(False)),
                Square(7, 1 ,Knight(False)),
                Square(7, 2 ,Bishop(False)),
                Square(7, 3 ,Queen(False)),
                Square(7, 4 ,King(False)),
                Square(7, 5 ,Bishop(False)),
                Square(7, 6 ,Knight(False)),
                Square(7, 7 ,Rook(False))]
        Board.board.append(line)

        
    def print_board() -> None:

        for x in Board.board[::-1]:
            for y in x:
                print(y, end=' ')
            print()

def has_path_rook(start: Square, end: Square) -> bool: #check if path is clear for rook

    #See if is a possible move
    if not start.piece.possible_move(start, end):
        return False

    x = end.x - start.x
    y = end.y - start.y

    #If moving in the same column
    if x != 0:
        for i in board_range(x):
            if not isinstance(Board.board[start.x + i][start.y].piece, EmptySquare):
                return False
        return True
    
    #Else, moving in the same line
    for i in board_range(y):
        if not isinstance(Board.board[start.x][start.y + i].piece, EmptySquare):
            return False
    return True

def has_path_bishop(start : Square, end : Square) -> bool: #check if path is clear for bishop

    if not start.piece.possible_move(start, end):
        return False
    
    x = end.x - start.x 
    y = end.y - start.y

    #verify this for the Queen move
    if x == 0 or y == 0:
        return False

    #Using zip because x and y absolute values are the same
    for i, j in zip(board_range(x), board_range(y)):
        if not isinstance(Board.board[start.x + i][start.y + j].piece, EmptySquare):
            return False
    return True


def pawn_can_capture(start : Square, end : Square) -> bool:

    x = end.x - start.x
    y = abs(end.y - start.y)

    if not isinstance(end.piece, EmptySquare) and start.piece.iswhite != end.piece.iswhite:
        if start.piece.iswhite and x == 1 and y == 1:
            return True
        elif not start.piece.iswhite and x == -1 and y == 1:
            return True
        
    #Checking for en passant
    if isinstance(end.piece, EmptySquare) and isinstance(Board.board[start.x][end.y].piece, Pawn):
        if start.piece.iswhite and y == 1 and x == 1:
            if Board.board[start.x][end.y].piece.en_passantable:
                return True 
        if not start.piece.iswhite and x == -1 and y == 1:
            if Board.board[start.x][end.y].piece.en_passantable:
                return True 
    return False


def can_castle(start : Square, end : Square) -> bool:

    x = end.x - start.x
    y = end.y - start.y

    if start.piece.moved or abs(y) != 2 or x != 0:
        return False
    
    #Find correct rook square and square rook will move to
    if y > 0:
        rook_square : Square = Board.board[start.x][7]
        move_square : Square = Board.board[start.x][start.y + 1]
    else:
        rook_square : Square = Board.board[start.x][0]
        move_square : Square = Board.board[start.x][start.y - 1]  
    
    #Verifies if rook_square is rook and has not moved
    if (not isinstance(rook_square.piece, Rook)) or rook_square.piece.moved == True:
        return False
    
    #Verifies path
    if has_path_rook(rook_square, move_square):
        move_piece(rook_square, move_square)
        return True
    return False


def _pawn_forward_path_clear(start: Square, end: Square) -> bool:
    """
    NEW: กันบั๊ก pawn เดิน 2 ช่องแล้วข้ามตัวหมาก
    ตรวจเฉพาะ "เดินตรง" (ไฟล์เดิม) เท่านั้น
    """
    if start.y != end.y:
        return True  # ไม่ใช่เดินตรง (capture จะตรวจที่อื่น)

    dx = end.x - start.x
    if start.piece.iswhite:
        if dx == 2:
            mid = Board.board[start.x + 1][start.y]
            return isinstance(mid.piece, EmptySquare)
    else:
        if dx == -2:
            mid = Board.board[start.x - 1][start.y]
            return isinstance(mid.piece, EmptySquare)
    return True


def move_piece(start: Square, end: Square) -> bool:

    # Move the rook
    if isinstance(start.piece, Rook):
        if has_path_rook(start, end):
            start.piece.moved = True
            Board.board[end.x][end.y].piece = start.piece
            Board.board[start.x][start.y] = Square(start.x, start.y)
            return True

    # Move the bishop
    elif isinstance(start.piece, Bishop):
        if has_path_bishop(start, end):
            Board.board[end.x][end.y].piece = start.piece
            Board.board[start.x][start.y] = Square(start.x, start.y)
            return True

    # Move the queen
    elif isinstance(start.piece, Queen):
        if has_path_rook(start, end):
            Board.board[end.x][end.y].piece = start.piece
            Board.board[start.x][start.y] = Square(start.x, start.y)
            return True
        elif has_path_bishop(start, end):
            Board.board[end.x][end.y].piece = start.piece
            Board.board[start.x][start.y] = Square(start.x, start.y)
            return True

    # Move the King 
    elif isinstance(start.piece, King):
        if start.piece.possible_move(start, end) or can_castle(start, end):
            start.piece.moved = True
            Board.board[end.x][end.y].piece = start.piece
            Board.board[start.x][start.y] = Square(start.x, start.y)
            return True

    # Move the knight
    elif isinstance(start.piece, Knight):
        if start.piece.possible_move(start, end):
            Board.board[end.x][end.y].piece = start.piece
            Board.board[start.x][start.y] = Square(start.x, start.y)
            return True

    # Move the pawn
    elif isinstance(start.piece, Pawn):
        # NEW: ถ้าเดินตรง 2 ช่อง ต้องไม่มีตัวขวาง
        if not _pawn_forward_path_clear(start, end):
            return False

        if ((start.piece.possible_move(start, end) and isinstance(end.piece, EmptySquare))
            or pawn_can_capture(start, end)):
            
            start.piece.moved = True

            if abs(start.x - end.x) == 2:
                start.piece.en_passantable = True
            
            # if en passant (capture เฉียงแต่ปลายทางว่าง)
            if isinstance(end.piece, EmptySquare) and start.y != end.y:
                Board.board[start.x][end.y] = Square(start.x, end.y)

            Board.board[end.x][end.y].piece = start.piece
            Board.board[start.x][start.y] = Square(start.x, start.y)
            return True
    return False


def main():
    Board.create_board()

    Board.board[1][0] = Square(1,0)
    Board.board[1][3] = Square(1,3)
    Board.board[6][3] = Square(6,3)
    Board.board[6][1] = Square(6,1)
    Board.print_board()

if __name__ == "__main__":
    main()