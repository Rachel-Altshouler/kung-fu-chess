from __future__ import annotations

import re


_SQUARE_RE = re.compile(r"^([a-h])([1-8])$", re.IGNORECASE)

#מנקה רווחים, מנסה להתאים לתבנית. אם לא תואם (למשל "z9" או "e") — זורק שגיאה ברורה עם הערך הבעייתי.
def square_to_coords(square: str, board_rows: int = 8) -> tuple[int, int]:
    match = _SQUARE_RE.match(square.strip())
    if match is None:
        raise ValueError(f"Invalid square: {square}")
    file_name, rank_name = match.group(1).lower(), match.group(2)
    col = ord(file_name) - ord("a")
    row = board_rows - int(rank_name)
    return row, col

#הפונקציה ההפוכה בדיוק — לוקחת קואורדינטות פנימיות וממירה בחזרה לסימון שחמט:
def coords_to_square(row: int, col: int, board_rows: int = 8) -> str:
    return f"{chr(ord('a') + col)}{board_rows - row}"
