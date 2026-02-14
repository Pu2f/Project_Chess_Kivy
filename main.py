from chess_core.rules import *
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import *
from kivy.core.window import Window
from kivy.properties import StringProperty

#   O app que vai rodar no kivy. Aqui cada parte do projeto se conecta e utilizado.
#   O tabuleiro em si é um gridLayout 8x8, e cada elemento do gridLayout é uma String property,
# podendo ser atualizado para alterar a imagem no tabuleiro.
#   O gridLayout está dentro de um boxLayout, e ao lado há uma imagem para representar o turno do
# jogador atual

Board.create_board()


class ChessGame(BoxLayout):
    pass


class BoardGrid(GridLayout):

    # ถ้า iswhite == True แสดงมุมมองจากฝั่งขาว (row 0 ที่ด้านล่างของ model)
    iswhite = True
    ui_iswhite = StringProperty("images/white-king.png")
    selected = False
    s_x = None  # เก็บพิกัด model ของ selection
    s_y = None

    w, h = Window._get_size()

    if w > h:
        board_size = h
    else:
        board_size = w
    row_force_default = True
    col_force_default = True
    row_default_height = board_size / 8
    col_default_width = board_size / 8

    # สร้าง properties สำหรับทุกช่อง (ค่าเริ่มต้นมาจาก model แต่จะถูกอัพเดตผ่าน update_images())
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
        """แปลงพิกัด UI (kv) เป็นพิกัด model (Board.board) ตามมุมมองปัจจุบัน"""
        if self.iswhite:
            return x, y
        return 7 - x, 7 - y

    def update_images(self):
        """อัพเดตทุก StringProperty ให้แม็ปจาก model ไปยัง UI ตามมุมมอง"""
        for ui_x in range(8):
            for ui_y in range(8):
                mx, my = self.ui_to_model(ui_x, ui_y)
                prop = f"s{ui_x}{ui_y}"
                # ทุกช่องเรียก get_selected_image() เพราะสถานะ selected ถูกเก็บบน piece ใน model
                setattr(self, prop, Board.board[mx][my].piece.get_selected_image())

    def click(self, x, y):
        # เมื่อผู้ใช้คลิกพิกัด UI ให้แปลงเป็นพิกัด model ก่อนใช้งาน
        mx, my = self.ui_to_model(x, y)

        if not BoardGrid.selected:
            # เลือกหมาก (เก็บพิกัดเป็น model coords)
            BoardGrid.s_x = mx
            BoardGrid.s_y = my
            BoardGrid.selected = True
            Board.board[mx][my].piece.selected = True

            self.update_images()

        else:
            # พยายามเดินจาก (s_x, s_y) -> (mx, my)
            if turn(BoardGrid.s_x, BoardGrid.s_y, mx, my, BoardGrid.iswhite):
                # ถ้าเดินสำเร็จ ให้สลับมุมมอง (เพราะเปลี่ยนตา)
                BoardGrid.iswhite = not BoardGrid.iswhite
                # สลับไอคอนแสดงว่าใครตา (UI ด้านข้าง)
                if self.ui_iswhite == "images/white-king.png":
                    self.ui_iswhite = "images/black-king.png"
                else:
                    self.ui_iswhite = "images/white-king.png"

            # ยกเลิก selected ทั้งคู่ (ใช้ model coords เดิม)
            BoardGrid.selected = False
            Board.board[BoardGrid.s_x][BoardGrid.s_y].piece.selected = False
            Board.board[mx][my].piece.selected = False

            # รีเฟรชภาพทั้งหมดตามมุมมองใหม่ (iswhite อาจเปลี่ยน)
            self.update_images()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 8
        # อัพเดตภาพเริ่มต้น (กรณี model เปลี่ยนก่อนหน้า)
        self.update_images()


class Ui(BoxLayout):
    w, h = Window._get_size()
    ui_size_x = max(w, h) - min(w, h)
    ui_size_y = min(w, h)
    ui_pos_x = min(w, h)


class ChessApp(App):
    pass


ChessApp().run()
