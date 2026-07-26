from __future__ import annotations

import re

from server.squares import square_to_coords


# Example: WQe2e5  /  BNf6g4  /  wPe2e4
_COMPACT_MOVE_RE = re.compile(
    r"^([WwBb])([KQRBNPkqrbnp])([a-h][1-8])([a-h][1-8])$",
)

#"תרגום" מטקסט חופשי שהמשתמש הקליד, לפורמט נתונים מובנה שהמערכת מבינה-לצבע למיקום ועוד.
def parse_compact_command(command: str, board_rows: int = 8) -> dict:
    text = command.strip().replace(" ", "")
    match = _COMPACT_MOVE_RE.match(text)
    if match is None:
        raise ValueError(
            "Invalid command. Use format like WQe2e5 "
            "(color + piece + from + to)."
        )

    color = match.group(1).lower()
    piece_type = match.group(2).upper()
    source = square_to_coords(match.group(3), board_rows)
    destination = square_to_coords(match.group(4), board_rows)
    token = f"{color}{piece_type}"

    return {
        "action": "MOVE",
        "token": token,
        "source": source,
        "destination": destination,
        "raw": text.upper() if text[0].isupper() else text,
    }
