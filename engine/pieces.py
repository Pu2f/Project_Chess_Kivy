# piece encoding: "." empty
# White: P N B R Q K
# Black: p n b r q k

UNICODE = {
    ".": "",
    "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
    "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚",
}

def piece_to_unicode(p: str) -> str:
    return UNICODE.get(p, "")

def is_white(p: str) -> bool:
    return p.isupper()

def is_black(p: str) -> bool:
    return p.islower()