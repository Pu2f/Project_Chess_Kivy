from engine.types import Position, Move

# IMPORTANT:
# ไฟล์นี้คือหัวใจ “ครบทุกกติกา”:
# - generate_pseudo_legal_moves
# - filter illegal (leave king in check)
# - castling legality
# - en passant legality (including discovered check cases)
# - promotion moves
# - check/checkmate/stalemate detection
# - draw rules: 50-move, repetition (ต้องใช้ zobrist), insufficient material

def generate_legal_moves(pos: Position) -> list[Move]:
    # TODO: ใส่เต็ม ๆ
    # ตอนนี้คืน list ว่างถ้าไม่อยากให้เดิน; แต่ UI จะดูเงียบเกิน
    # เพื่อให้ลองคลิกแล้วเดินได้ เราจะ “ชั่วคราว” สร้าง move แบบ naive (ไม่ครบกติกา)
    # คุณบอกฉันว่าต้องการส่ง engine เต็มทีเดียวหรือทยอยส่งพร้อมเทสต์
    moves = []
    stm_white = pos.side_to_move == "w"
    for from_sq, p in enumerate(pos.board):
        if p == ".":
            continue
        if stm_white and not p.isupper():
            continue
        if (not stm_white) and not p.islower():
            continue
        # naive: เดินไป 1 ช่องรอบตัว (เพื่อเดโม)
        fr = from_sq // 8
        ff = from_sq % 8
        for dr in (-1, 0, 1):
            for df in (-1, 0, 1):
                if dr == 0 and df == 0:
                    continue
                tr = fr + dr
                tf = ff + df
                if 0 <= tr < 8 and 0 <= tf < 8:
                    to_sq = tr * 8 + tf
                    moves.append(Move(from_sq=from_sq, to_sq=to_sq))
    return moves

def is_in_check(pos: Position, side: str) -> bool:
    # TODO: ทำจริง: หา king square + attacked squares
    return False