from model.constants import BoardConstants


class Piece:
    #יוצרת כלי
    def __init__(self, color: str, piece_type: str):
        self.color = color
        self.piece_type = piece_type

    #ממירה מחרוזת לאובייקט
    @staticmethod
    def from_token(token: str):
        if token == BoardConstants.EMPTY_CELL:
            return None
        return Piece(token[0], token[1])

    #ממירה את הכלי חזרה למחרוזת
    def to_token(self) -> str:
        return f"{self.color}{self.piece_type}"

    #בודקת אם 2 כלים באותו צבע
    def is_same_color(self, other: "Piece") -> bool:
        return self.color == other.color
