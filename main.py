from chess_core.rules import *
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import StringProperty
from images import *

# init model
Board.create_board()


class ChessGame(BoxLayout):
    pass


class BoardGrid(GridLayout):

    cols = 8
    rows = 8
    
    # มุมมองปัจจุบัน
    iswhite = True
    ui_iswhite = StringProperty("images/white-king.png")

    # selection state
    selected = False
    s_x = None
    s_y = None

    # move list (SAN) แสดงด้านขวา
    move_list_text = StringProperty("")

    w, h = Window._get_size()
    board_size = h if w > h else w

    row_force_default = True
    col_force_default = True
    row_default_height = board_size / 8
    col_default_width = board_size / 8



    def clear_hints(self):
        self.update_images()



    def show_hints(self, mx, my):
            self.clear_hints() # ล้างสถานะเก่าก่อน

            from chess_core.board import has_path_rook, has_path_bishop, pawn_can_capture
            from chess_core.pieces import Rook, Bishop, Queen, Knight, King, Pawn
            from chess_core.square import EmptySquare

            start_square = Board.board[mx][my]
            piece = start_square.piece

            # วนลูปตรวจสอบทุกช่องในกระดาน
            for r in range(8):
                for c in range(8):
                    if r == mx and c == my:
                        continue

                    end_square = Board.board[r][c]
                    target_piece = end_square.piece
                    legal = False

                    # ตรวจสอบกฎการเดินตามประเภทของหมาก
                    if isinstance(piece, Rook):
                        legal = has_path_rook(start_square, end_square)
                    elif isinstance(piece, Bishop):
                        legal = has_path_bishop(start_square, end_square)
                    elif isinstance(piece, Queen):
                        legal = has_path_rook(start_square, end_square) or has_path_bishop(start_square, end_square)
                    elif isinstance(piece, Knight):
                        legal = piece.possible_move(start_square, end_square)
                    elif isinstance(piece, King):
                        # รวมการเดินปกติและการ Castle
                        from chess_core.board import can_castle
                        legal = piece.possible_move(start_square, end_square) or can_castle(start_square, end_square)
                    elif isinstance(piece, Pawn):
                        # เดินไปที่ว่าง
                        if piece.possible_move(start_square, end_square) and isinstance(target_piece, EmptySquare):
                            legal = True
                        # เดินไปกิน (รวม En Passant)
                        elif pawn_can_capture(start_square, end_square):
                            legal = True

                    if legal:
                        # ตั้งค่าสถานะ hint หรือ capture ใน Model
                        if isinstance(target_piece, EmptySquare):
                            # กรณีเดินไปช่องว่าง หรือกิน En Passant (ช่องที่คลิกอาจจะว่าง)
                            # ตรวจสอบ En Passant เพิ่มเติมเพื่อให้จุดแสดงถูกช่อง
                            if isinstance(piece, Pawn) and pawn_can_capture(start_square, end_square) and isinstance(target_piece, EmptySquare):
                                Board.board[r][c].piece.capture = True
                            else:
                                Board.board[r][c].piece.hint = True
                        else:
                            Board.board[r][c].piece.capture = True

    def is_hint(self, x, y):
        mx, my = self.ui_to_model(x, y)
        return getattr(Board.board[mx][my].piece, 'hint', False)

    def is_capture(self, x, y):
        mx, my = self.ui_to_model(x, y)
        return getattr(Board.board[mx][my].piece, 'capture', False)

    def clear_hints(self):
        """ล้างสถานะจุดสีทั้งหมดบนกระดาน"""
        for x in range(8):
            for y in range(8):
                Board.board[x][y].piece.hint = False
                Board.board[x][y].piece.capture = False

    # 8x8 image properties
    s00 = StringProperty(Board.board[0][0].piece.image)
    s01 = StringProperty(Board.board[0][1].piece.image)
    s02 = StringProperty(Board.board[0][2].piece.image)
    s03 = StringProperty(Board.board[0][3].piece.image)
    s04 = StringProperty(Board.board[0][4].piece.image)
    s05 = StringProperty(Board.board[0][5].piece.image)
    s06 = StringProperty(Board.board[0][6].piece.image)
    s07 = StringProperty(Board.board[0][7].piece.image)

    s10 = StringProperty(Board.board[1][0].piece.image)
    s11 = StringProperty(Board.board[1][1].piece.image)
    s12 = StringProperty(Board.board[1][2].piece.image)
    s13 = StringProperty(Board.board[1][3].piece.image)
    s14 = StringProperty(Board.board[1][4].piece.image)
    s15 = StringProperty(Board.board[1][5].piece.image)
    s16 = StringProperty(Board.board[1][6].piece.image)
    s17 = StringProperty(Board.board[1][7].piece.image)

    s20 = StringProperty(Board.board[2][0].piece.image)
    s21 = StringProperty(Board.board[2][1].piece.image)
    s22 = StringProperty(Board.board[2][2].piece.image)
    s23 = StringProperty(Board.board[2][3].piece.image)
    s24 = StringProperty(Board.board[2][4].piece.image)
    s25 = StringProperty(Board.board[2][5].piece.image)
    s26 = StringProperty(Board.board[2][6].piece.image)
    s27 = StringProperty(Board.board[2][7].piece.image)

    s30 = StringProperty(Board.board[3][0].piece.image)
    s31 = StringProperty(Board.board[3][1].piece.image)
    s32 = StringProperty(Board.board[3][2].piece.image)
    s33 = StringProperty(Board.board[3][3].piece.image)
    s34 = StringProperty(Board.board[3][4].piece.image)
    s35 = StringProperty(Board.board[3][5].piece.image)
    s36 = StringProperty(Board.board[3][6].piece.image)
    s37 = StringProperty(Board.board[3][7].piece.image)

    s40 = StringProperty(Board.board[4][0].piece.image)
    s41 = StringProperty(Board.board[4][1].piece.image)
    s42 = StringProperty(Board.board[4][2].piece.image)
    s43 = StringProperty(Board.board[4][3].piece.image)
    s44 = StringProperty(Board.board[4][4].piece.image)
    s45 = StringProperty(Board.board[4][5].piece.image)
    s46 = StringProperty(Board.board[4][6].piece.image)
    s47 = StringProperty(Board.board[4][7].piece.image)

    s50 = StringProperty(Board.board[5][0].piece.image)
    s51 = StringProperty(Board.board[5][1].piece.image)
    s52 = StringProperty(Board.board[5][2].piece.image)
    s53 = StringProperty(Board.board[5][3].piece.image)
    s54 = StringProperty(Board.board[5][4].piece.image)
    s55 = StringProperty(Board.board[5][5].piece.image)
    s56 = StringProperty(Board.board[5][6].piece.image)
    s57 = StringProperty(Board.board[5][7].piece.image)

    s60 = StringProperty(Board.board[6][0].piece.image)
    s61 = StringProperty(Board.board[6][1].piece.image)
    s62 = StringProperty(Board.board[6][2].piece.image)
    s63 = StringProperty(Board.board[6][3].piece.image)
    s64 = StringProperty(Board.board[6][4].piece.image)
    s65 = StringProperty(Board.board[6][5].piece.image)
    s66 = StringProperty(Board.board[6][6].piece.image)
    s67 = StringProperty(Board.board[6][7].piece.image)

    s70 = StringProperty(Board.board[7][0].piece.image)
    s71 = StringProperty(Board.board[7][1].piece.image)
    s72 = StringProperty(Board.board[7][2].piece.image)
    s73 = StringProperty(Board.board[7][3].piece.image)
    s74 = StringProperty(Board.board[7][4].piece.image)
    s75 = StringProperty(Board.board[7][5].piece.image)
    s76 = StringProperty(Board.board[7][6].piece.image)
    s77 = StringProperty(Board.board[7][7].piece.image)

    def ui_to_model(self, x, y):
        if self.iswhite:
            return x, y
        return 7 - x, 7 - y

    def update_images(self):
        for ui_x in range(8):
            for ui_y in range(8):
                mx, my = self.ui_to_model(ui_x, ui_y)
                prop = f"s{ui_x}{ui_y}"
                setattr(self, prop, Board.board[mx][my].piece.get_selected_image())

    def click(self, x, y):
            mx, my = self.ui_to_model(x, y)

            if not BoardGrid.selected:
                # ถ้าเลือกหมากฝั่งตัวเอง
                if Board.board[mx][my].piece.iswhite == BoardGrid.iswhite:
                    BoardGrid.s_x = mx
                    BoardGrid.s_y = my
                    BoardGrid.selected = True
                    Board.board[mx][my].piece.selected = True
                    
                    # แสดงจุดเขียว/แดง
                    self.show_hints(mx, my)
                    
                    self.update_images()
                return

            # พยายามเดินหมาก
            moved = turn(BoardGrid.s_x, BoardGrid.s_y, mx, my, BoardGrid.iswhite)

            if moved:
                BoardGrid.iswhite = not BoardGrid.iswhite
                self.ui_iswhite = (
                    "images/black-king.png"
                    if self.ui_iswhite == "images/white-king.png"
                    else "images/white-king.png"
                )

            # เคลียร์สถานะหลังเดินหรือยกเลิก
            self.clear_hints() # ล้างจุดสีทั้งหมด
            BoardGrid.selected = False
            Board.board[BoardGrid.s_x][BoardGrid.s_y].piece.selected = False
            self.update_images()
            self.move_list_text = SAN_HISTORY.formatted()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 8
        self.update_images()
        self.move_list_text = SAN_HISTORY.formatted()


class Ui(BoxLayout):
    w, h = Window._get_size()
    ui_size_x = max(w, h) - min(w, h)
    ui_size_y = min(w, h)
    ui_pos_x = min(w, h)


class ChessApp(App):
    pass


ChessApp().run()