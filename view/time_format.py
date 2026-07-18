from __future__ import annotations

from model.constants import Colors


def format_game_clock(milliseconds: int) -> str:
    ms = max(0, int(milliseconds))
    minutes, remainder = divmod(ms, 60_000)
    seconds, millis = divmod(remainder, 1000)
    tenths = millis // 100

    if minutes >= 60:
        hours, minutes = divmod(minutes, 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    if minutes > 0:
        return f"{minutes:02d}:{seconds:02d}"

    return f"{seconds}.{tenths}"


def format_score_seconds(total_seconds: int) -> str:
    total_seconds = max(0, int(total_seconds))
    minutes, seconds = divmod(total_seconds, 60)
    if minutes > 0:
        return f"{minutes}:{seconds:02d} sec"
    return f"{seconds} sec"


def player_name_hebrew(color: str | None) -> str:
    if color == Colors.WHITE:
        return "לבן"
    if color == Colors.BLACK:
        return "שחור"
    return "לא ידוע"


def player_name_english(color: str | None) -> str:
    if color == Colors.WHITE:
        return "White"
    if color == Colors.BLACK:
        return "Black"
    return "Unknown"
