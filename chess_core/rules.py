from chess_core.pieces import *
from chess_core.square import *
from chess_core.board import *

from chess_core.fen import to_fen
from chess_core.san_history import SanHistory

# เก็บ SAN history ไว้ใช้ใน UI
SAN_HISTORY = SanHistory()

#   Neste módulo, temos regras do jogo em si, como checks, checkmates, promoções e os turnos.
#   Com algumas pequenas modificações, é possível jogar o jogo neste módulo, através do terminal.

def clear_legal_hints() -> None:
    for line in Board.board:
        for sq in line:
            sq.legal_move = False
            sq.legal_capture = False
            sq.legal_castle = False


def compute_legal_hints_for(x: int, y: int, iswhite: bool) -> None:
    """
    ตั้งค่า flag legal_move / legal_capture / legal_castle ใ���้ Board.board
    โดยคำนวณจากกติกาจริง: เดินแล้วห้ามทำให้คิงตัวเองโดนเช็ค
    """
    clear_legal_hints()

    start: Square = Board.board[x][y]
    if isinstance(start.piece, EmptySquare):
        return
    if start.piece.iswhite != iswhite:
        return

    for tx in range(8):
        for ty in range(8):
            if tx == x and ty == y:
                continue

            end: Square = Board.board[tx][ty]

            # snapshot สภาพก่อนลองเดิน (ขั้นต่ำที่จำเป็น)
            s_piece = start.piece
            e_piece = end.piece
            s_moved = getattr(s_piece, "moved", None)
            e_moved = getattr(e_piece, "moved", None)

            # สำหรับ pawn: ต้องจำ en_passantable ด้วย
            s_ep = getattr(s_piece, "en_passantable", None)
            side_sq = None
            side_piece = None
            side_moved = None
            side_ep = None

            # เผื่อ en passant: ถ้าปลายทางว่างและเป็น pawn capture pattern
            if isinstance(s_piece, Pawn) and isinstance(e_piece, EmptySquare) and pawn_can_capture(start, end):
                side_sq = Board.board[x][ty]
                side_piece = side_sq.piece
                side_moved = getattr(side_piece, "moved", None)
                side_ep = getattr(side_piece, "en_passantable", None)

            moved = move_piece(start, end)
            if not moved:
                # restore (กันหลุดกรณีโค้ด move_piece เปลี่ยนอะไรแล้ว return False—โดยปกติไม่ควร)
                start.piece = s_piece
                end.piece = e_piece
                if s_moved is not None:
                    start.piece.moved = s_moved
                if e_moved is not None and not isinstance(end.piece, EmptySquare):
                    end.piece.moved = e_moved
                if s_ep is not None and isinstance(start.piece, Pawn):
                    start.piece.en_passantable = s_ep
                if side_sq is not None:
                    side_sq.piece = side_piece
                    if side_moved is not None and not isinstance(side_sq.piece, EmptySquare):
                        side_sq.piece.moved = side_moved
                    if side_ep is not None and isinstance(side_sq.piece, Pawn):
                        side_sq.piece.en_passantable = side_ep
                continue

            illegal = check_for_check(iswhite)

            # revert board กลับเหมือนเดิม
            Board.board[x][y].piece = s_piece
            Board.board[tx][ty].piece = e_piece
            Board.board[x][y].piece.moved = s_moved
            if not isinstance(Board.board[tx][ty].piece, EmptySquare) and e_moved is not None:
                Board.board[tx][ty].piece.moved = e_moved

            if isinstance(Board.board[x][y].piece, Pawn) and s_ep is not None:
                Board.board[x][y].piece.en_passantable = s_ep

            if side_sq is not None:
                side_sq.piece = side_piece
                if not isinstance(side_sq.piece, EmptySquare) and side_moved is not None:
                    side_sq.piece.moved = side_moved
                if isinstance(side_sq.piece, Pawn) and side_ep is not None:
                    side_sq.piece.en_passantable = side_ep

            if illegal:
                continue

            # mark hint
            is_castle = isinstance(s_piece, King) and (abs(ty - y) == 2) and (tx == x)
            if is_castle:
                Board.board[tx][ty].legal_castle = True
            elif isinstance(e_piece, EmptySquare):
                Board.board[tx][ty].legal_move = True
            else:
                Board.board[tx][ty].legal_capture = True


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