from __future__ import annotations

import json
from typing import Any

#פונקציה שבונה הודעת JSON לשליחה
def encode_message(message_type: str, **payload) -> str:
    body = {"type": message_type}
    body.update(payload)
    return json.dumps(body)

#הפעולה ההפוכה — הופכת מחרוזת JSON חזרה למילון פייתון
def decode_message(raw: str) -> dict[str, Any]:
    data = json.loads(raw)
    if not isinstance(data, dict) or "type" not in data:
        raise ValueError("Message must be a JSON object with a 'type' field.")
    return data

#ממירה אובייקט "תמונת מצב" מלא של המשחק למילון "שטוח" שאפשר לשלוח כ-JSON
def snapshot_to_dict(snapshot) -> dict[str, Any]:
    pieces = []
    for piece in snapshot.pieces:
        movement = piece.get("movement")
        piece_data = {
            "token": piece["token"],
            "row": piece["row"],
            "col": piece["col"],
        }
        if movement is not None:
            piece_data["movement"] = {
                "id": movement.movement_id,
                "source": list(movement.source),
                "destination": list(movement.destination),
                "start_time": movement.start_time,
                "finish_time": movement.finish_time,
                "is_jump": movement.is_jump,
            }
        pieces.append(piece_data)

    move_log = []
    for record in getattr(snapshot, "move_log", []):
        move_log.append(
            {
                "piece_token": record.piece_token,
                "color": record.color,
                "source": list(record.source),
                "destination": list(record.destination),
                "start_time": record.start_time,
                "finish_time": record.finish_time,
                "is_jump": record.is_jump,
                "captured_token": record.captured_token,
                "text": record.as_text(),
            }
        )

    selected = snapshot.selected_position
    if selected is not None and hasattr(selected, "as_tuple"):
        selected = list(selected.as_tuple())
    elif selected is not None:
        selected = list(selected)

    return {
        "clock": snapshot.clock,
        "white_score": snapshot.white_score,
        "black_score": snapshot.black_score,
        "rows": snapshot.rows,
        "cols": snapshot.cols,
        "selected_position": selected,
        "game_over": snapshot.game_over,
        "winner": snapshot.winner,
        "is_stalemate": snapshot.is_stalemate,
        "pieces": pieces,
        "move_log": move_log,
        "board": _board_tokens_from_pieces(snapshot),
    }


def snapshot_from_dict(data: dict[str, Any]):
    from domain.game_snapshot import GameSnapshot
    from domain.move_log import MoveRecord
    from domain.piece import Piece
    from realtime.motion import Motion

    rows = int(data.get("rows", 8))
    cols = int(data.get("cols", 8))
    pieces = []
    for piece in data.get("pieces") or []:
        movement = None
        mov = piece.get("movement")
        if mov is not None:
            source = tuple(mov["source"])
            destination = tuple(mov["destination"])
            token = piece["token"]
            piece_obj = Piece.from_token(token)
            piece_type = piece_obj.piece_type if piece_obj is not None else "P"
            is_jump = bool(mov.get("is_jump"))
            start_time = int(mov["start_time"])
            path = Motion.build_path(
                piece_type, source, destination, start_time, is_jump
            )
            movement = Motion(
                mov["id"],
                token,
                source,
                destination,
                start_time,
                int(mov["finish_time"]),
                path,
                is_jump,
            )
        pieces.append(
            {
                "token": piece["token"],
                "row": piece["row"],
                "col": piece["col"],
                "movement": movement,
            }
        )

    move_log = []
    for record in data.get("move_log") or []:
        move_log.append(
            MoveRecord(
                piece_token=record["piece_token"],
                source=tuple(record["source"]),
                destination=tuple(record["destination"]),
                start_time=int(record["start_time"]),
                finish_time=int(record["finish_time"]),
                is_jump=bool(record.get("is_jump")),
                captured_token=record.get("captured_token"),
                board_rows=rows,
            )
        )

    selected = data.get("selected_position")
    if selected is not None:
        selected = tuple(selected)

    return GameSnapshot(
        clock=int(data.get("clock", 0)),
        white_score=int(data.get("white_score", 0)),
        black_score=int(data.get("black_score", 0)),
        pieces=pieces,
        rows=rows,
        cols=cols,
        selected_position=selected,
        game_over=bool(data.get("game_over")),
        winner=data.get("winner"),
        is_stalemate=bool(data.get("is_stalemate")),
        move_log=move_log,
    )


def _board_tokens_from_pieces(snapshot) -> list[list[str]]:
    grid = [["." for _ in range(snapshot.cols)] for _ in range(snapshot.rows)]
    for piece in snapshot.pieces:
        if piece.get("movement") is not None:
            continue
        row = int(round(piece["row"]))
        col = int(round(piece["col"]))
        if 0 <= row < snapshot.rows and 0 <= col < snapshot.cols:
            grid[row][col] = piece["token"]
    return grid
