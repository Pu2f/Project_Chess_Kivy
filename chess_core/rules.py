from chess_core.pieces import *
from chess_core.square import *
from chess_core.board import *

from chess_core.fen import to_fen
from chess_core.san_history import SanHistory

# เก็บ SAN history ไว้ใช้ใน UI
SAN_HISTORY = SanHistory()

#   Neste módulo, temos regras do jogo em si, como checks, checkmates, promoções e os turnos.
#   Com algumas pequenas modificações, é possível jogar o jogo neste módulo, através do terminal.

def check_for_check(iswhite: bool) -> bool:
    # find the king
    king_square = None
    for line in Board.board:
        for square in line:
            if isinstance(square.piece, King) and square.piece.iswhite == iswhite:
                king_square = square
                break
        if king_square:
            break

    if king_square is None:
        return False

    # check if any piece has a path to the king
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


def end_turn(iswhite: bool) -> None:
    # reset en_passantable ของฝ่ายตรงข้าม (ถูกต้อง: มีผล 1 ตา)
    for line in Board.board:
        for square in line:
            if square.piece.iswhite != iswhite and isinstance(square.piece, Pawn):
                square.piece.en_passantable = False

    # promotions (โปรเจกต์คุณ promote เป็น Queen เสมอ)
    line = 7 if iswhite else 0
    for square in Board.board[line]:
        if isinstance(square.piece, Pawn):
            square.piece = Queen(iswhite)


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

                    if turn(a, b, c, d, iswhite, True):
                        Board.board[c][d].piece = end_piece
                        Board.board[a][b].piece = start_piece
                        return False

                    # garantees en_passantable correct
                    if hasattr(Board.board[a][b].piece, "en_passantable"):
                        Board.board[a][b].piece.en_passantable = False
    return True


def turn(x1, y1, x2, y2, iswhite, check=False):
    start: Square = Board.board[x1][y1]
    end: Square = Board.board[x2][y2]

    # FEN ก่อนเดิน เพื่อให้ python-chess สร้าง SAN ถูกเต็มกติกา
    fen_before = to_fen(side_to_move_iswhite=iswhite)

    # select the pieces to reverse movement if check
    s_piece = start.piece
    e_piece = end.piece

    # save piece movement property
    s_moved = s_piece.moved
    e_moved = e_piece.moved

    if start.piece.iswhite == iswhite:
        if move_piece(start, end):
            # if move creates check in its own king, it's illegal
            if check_for_check(iswhite):
                # reverse movement
                Board.board[start.x][start.y].piece = s_piece
                Board.board[end.x][end.y].piece = e_piece
                Board.board[start.x][start.y].piece.moved = s_moved
                Board.board[end.x][end.y].piece.moved = e_moved
                return False

            # promotion flag สำหรับ SAN (python-chess ต้องรู้ก่อน)
            promotion = None
            moved_piece = Board.board[x2][y2].piece
            if isinstance(moved_piece, Pawn):
                if (iswhite and x2 == 7) or ((not iswhite) and x2 == 0):
                    promotion = "q"

            # บันทึก SAN (ก่อน end_turn ที่จะเปลี่ยนชิ้นบนกระดาน)
            SAN_HISTORY.push_from_fen_and_coords(
                fen_before_move=fen_before,
                x1=x1, y1=y1, x2=x2, y2=y2,
                promotion=promotion,
            )

            # promotions and reset en_passantable
            end_turn(iswhite)

            # check for checkmate on enemy king
            other_iswhite = not iswhite
            if check_for_check(other_iswhite):
                if check_for_checkmate(other_iswhite):
                    # if checkmate, mated king becomes red
                    for i in range(64):
                        if (
                            isinstance(Board.board[i // 8][i % 8].piece, King)
                            and Board.board[i // 8][i % 8].piece.iswhite == other_iswhite
                        ):
                            Board.board[i // 8][i % 8].piece.selected = True
            return True
    return False


def main():
    Board.create_board()
    Board.print_board()


if __name__ == "__main__":
    main()