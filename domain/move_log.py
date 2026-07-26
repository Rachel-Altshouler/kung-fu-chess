from __future__ import annotations

from domain.piece import Piece


class MoveRecord:
    def __init__(
        self,
        piece_token: str,
        source: tuple[int, int],
        destination: tuple[int, int],
        start_time: int,
        finish_time: int,
        is_jump: bool = False,
        captured_token: str | None = None,
        board_rows: int = 8,
    ):
        self.piece_token = piece_token
        self.source = source
        self.destination = destination
        self.start_time = start_time
        self.finish_time = finish_time
        self.is_jump = is_jump
        self.captured_token = captured_token
        self.board_rows = board_rows

        piece = Piece.from_token(piece_token)
        self.color = piece.color if piece is not None else None

    #— ממירה קואורדינטות פנימיות (row, col) לסימון שחמט סטנדרטי (כמו "e4"):
    def square_name(self, position: tuple[int, int]) -> str:
        row, col = position
        file_name = chr(ord("a") + col)
        rank_name = str(self.board_rows - row)
        return f"{file_name}{rank_name}"

    def as_text(self) -> str:
        action = "jump" if self.is_jump else "move"
        text = (
            f"{self.piece_token} {action} "
            f"{self.square_name(self.source)}→{self.square_name(self.destination)}"
        )
        if self.captured_token:
            text += f" x{self.captured_token}"
        return text


class MoveLog:
    def __init__(self):
        self._records: list[MoveRecord] = []

    def add(self, record: MoveRecord):
        self._records.append(record)

    def get_all(self) -> list[MoveRecord]:
        return list(self._records)

    def get_for_color(self, color: str) -> list[MoveRecord]:
        return [record for record in self._records if record.color == color]

    def clear(self):
        self._records.clear()