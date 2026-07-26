"""
Networked shared-board client.
Each player runs this on their own computer, creates/joins the same Room ID,
and both play on one server board (synced over FastAPI WebSocket).
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import websockets

KUNG_FU_ROOT = Path(__file__).resolve().parent.parent
if str(KUNG_FU_ROOT) not in sys.path:
    sys.path.insert(0, str(KUNG_FU_ROOT))

import bootstrap  # noqa: F401

from bus import Events, create_event_system
from client.display_sync import DisplayClock, apply_smooth_positions, token_at_square
from client.home_screen import login_prompt, room_prompt
from client.logging_util import setup_client_logger
from domain.constants import BoardConstants, GraphicsConstants
from rendering.renderer import Renderer
from server.protocol import decode_message, encode_message, snapshot_from_dict

logger = setup_client_logger()


class _BoardBounds:
    def __init__(self, rows: int, cols: int):
        self._rows = rows
        self._cols = cols

    def is_within_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self._rows and 0 <= col < self._cols


@dataclass
class ClientContext:
    logged_in: bool = False
    in_game: bool = False
    my_role: str | None = None
    my_rating: int | None = None
    room_id: str | None = None
    players: list = field(default_factory=list)
    state: dict | None = None
    status_line: str = "Connecting..."
    game_ready: asyncio.Event = field(default_factory=asyncio.Event)
    selected: tuple[int, int] | None = None
    websocket: object | None = None
    display_clock: DisplayClock = field(default_factory=DisplayClock)
    seen_movements: set = field(default_factory=set)
    last_scores: tuple[int, int] = (0, 0)
    game_over_announced: bool = False
    bus: object | None = None
    sound: object | None = None


def _owns_piece(token: str, role: str | None) -> bool:
    if not token or token == BoardConstants.EMPTY_CELL:
        return False
    color = token[0].upper()
    if role == "white":
        return color == "W"
    if role == "black":
        return color == "B"
    return False


def _publish_move_sounds(ctx: ClientContext, state: dict):
    if ctx.bus is None or not state:
        return
    for piece in state.get("pieces") or []:
        mov = piece.get("movement")
        if not mov:
            continue
        mid = mov.get("id") if isinstance(mov, dict) else None
        if mid is None or mid in ctx.seen_movements:
            continue
        ctx.seen_movements.add(mid)
        ctx.bus.publish(Events.PIECE_MOVED, {"token": piece.get("token")})

    white = int(state.get("white_score", 0))
    black = int(state.get("black_score", 0))
    prev_w, prev_b = ctx.last_scores
    if white > prev_w or black > prev_b:
        ctx.bus.publish(Events.PIECE_CAPTURED, {})
    ctx.last_scores = (white, black)


def _apply_state(ctx: ClientContext, state: dict | None):
    if not state:
        return
    ctx.state = state
    ctx.display_clock.sync(int(state.get("clock", 0)))
    _publish_move_sounds(ctx, state)


async def _handle_message(message: dict, ctx: ClientContext):
    mtype = message.get("type")
    logger.info("recv type=%s", mtype)

    if mtype == "login_ok":
        ctx.logged_in = True
        ctx.my_rating = message.get("rating")
        ctx.status_line = "Logged in — create or join a room"
    elif mtype == "login_denied":
        ctx.status_line = f"Login failed: {message.get('detail')}"
    elif mtype == "room_created":
        ctx.room_id = message.get("room_id")
        ctx.my_role = message.get("role")
        ctx.players = message.get("players") or []
        _apply_state(ctx, message.get("state"))
        ctx.status_line = (
            f"Room {ctx.room_id} — you are WHITE. "
            f"Send this Room ID to your friend and wait..."
        )
        print(f"\n*** ROOM ID: {ctx.room_id}  (share with your friend) ***\n")
    elif mtype == "room_joined":
        ctx.room_id = message.get("room_id")
        ctx.my_role = message.get("role")
        ctx.players = message.get("players") or []
        _apply_state(ctx, message.get("state"))
        if message.get("waiting"):
            ctx.status_line = f"Joined room {ctx.room_id} as {ctx.my_role} — waiting..."
        else:
            ctx.in_game = True
            ctx.game_ready.set()
    elif mtype == "game_started":
        ctx.in_game = True
        ctx.room_id = message.get("room_id") or ctx.room_id
        ctx.my_role = message.get("role") or ctx.my_role
        ctx.players = message.get("players") or []
        ctx.selected = None
        ctx.seen_movements.clear()
        ctx.game_over_announced = False
        _apply_state(ctx, message.get("state"))
        opponent = message.get("opponent") or "?"
        ctx.status_line = (
            f"Room {ctx.room_id} — you are {(ctx.my_role or '?').upper()} "
            f"vs {opponent} (same board)"
        )
        ctx.game_ready.set()
    elif mtype == "player_joined":
        ctx.players = message.get("players") or ctx.players
        ctx.status_line = (
            f"{message.get('username')} joined as {message.get('role')} "
            f"({len(ctx.players)}/2)"
        )
    elif mtype == "player_left":
        ctx.players = message.get("players") or ctx.players
        ctx.status_line = f"{message.get('username')} left the room"
        ctx.in_game = len(ctx.players) >= 2
    elif mtype == "state":
        ctx.room_id = message.get("room_id") or ctx.room_id
        ctx.players = message.get("players") or ctx.players
        _apply_state(ctx, message.get("state"))
        if (
            ctx.state
            and ctx.state.get("game_over")
            and not ctx.game_over_announced
        ):
            ctx.game_over_announced = True
            winner = ctx.state.get("winner")
            ctx.status_line = f"Game over — winner: {winner or 'draw'}"
    elif mtype == "ack" and not message.get("ok"):
        ctx.status_line = message.get("detail") or "Move rejected"
    elif mtype == "error":
        ctx.status_line = message.get("message") or "Error"
        print(f"ERROR: {ctx.status_line}")


async def _receiver(websocket, inbox: asyncio.Queue):
    async for raw in websocket:
        await inbox.put(decode_message(raw))


async def _process_inbox(inbox: asyncio.Queue, ctx: ClientContext):
    while True:
        await _handle_message(await inbox.get(), ctx)


async def _enter_room(websocket, ctx: ClientContext) -> bool:
    action, room_id = room_prompt()
    if action == "quit":
        return False

    ctx.game_ready.clear()
    ctx.in_game = False

    if action == "create":
        await websocket.send(encode_message("create_room"))
        print("Waiting for your friend to join with the Room ID...")
        try:
            await asyncio.wait_for(ctx.game_ready.wait(), timeout=600)
        except asyncio.TimeoutError:
            print("Timed out waiting for friend.")
            return False
        return ctx.in_game

    await websocket.send(encode_message("join_room", room_id=room_id))
    try:
        await asyncio.wait_for(ctx.game_ready.wait(), timeout=30)
    except asyncio.TimeoutError:
        print("Could not join room / start game. Check Room ID and server.")
        return False
    return ctx.in_game


async def _graphics_loop(ctx: ClientContext):
    renderer = Renderer()
    role = (ctx.my_role or "?").upper()
    # ASCII-only name — one OpenCV window (no pygame / no second board)
    window_name = f"KungFuChess-{role}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    pending_clicks: list[tuple[int, int, int]] = []
    frame_delay = GraphicsConstants.FRAME_DELAY_MS / 1000.0

    def on_mouse(event, x, y, flags, param):
        if event in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN):
            pending_clicks.append((event, x, y))

    cv2.setMouseCallback(window_name, on_mouse)

    async def handle_click(event, x, y):
        if not ctx.state or ctx.state.get("game_over"):
            return
        rows = int(ctx.state.get("rows", 8))
        cols = int(ctx.state.get("cols", 8))
        pos = Renderer.pixel_to_board_position(_BoardBounds(rows, cols), x, y)
        if pos is None:
            return

        row, col = pos
        token = token_at_square(ctx.state, row, col)

        if event == cv2.EVENT_RBUTTONDOWN:
            target = ctx.selected or (row, col)
            if ctx.selected or _owns_piece(token, ctx.my_role):
                await ctx.websocket.send(
                    encode_message("jump", source=list(target))
                )
            ctx.selected = None
            return

        if ctx.selected is None:
            if token != BoardConstants.EMPTY_CELL and _owns_piece(token, ctx.my_role):
                ctx.selected = (row, col)
            return

        src = ctx.selected
        ctx.selected = None
        if src != (row, col):
            await ctx.websocket.send(
                encode_message("command", source=list(src), destination=[row, col])
            )

    print(
        f"ONE shared board (Room {ctx.room_id}). "
        f"You control {role} only — friend's moves appear here automatically."
    )

    try:
        while ctx.in_game:
            # Let WebSocket receiver update shared state between frames
            await asyncio.sleep(0)

            while pending_clicks:
                e, x, y = pending_clicks.pop(0)
                await handle_click(e, x, y)

            if ctx.state:
                snap = snapshot_from_dict(ctx.state)
                apply_smooth_positions(snap, ctx.display_clock.now())
                snap.selected_position = None
                canvas = renderer.render(snap)
                line = (
                    f"SHARED board Room {ctx.room_id} | You: {role} | "
                    f"Friend moves show here | move YOUR pieces only"
                )
                canvas.put_text(
                    line,
                    GraphicsConstants.SIDE_PANEL_WIDTH + 10,
                    58,
                    0.38,
                    color=(180, 220, 255, 255),
                    thickness=1,
                )
                cv2.resizeWindow(
                    window_name, canvas.img.shape[1], canvas.img.shape[0]
                )
                # waitKey(1) so asyncio can sync opponent moves (not blocked 30ms)
                key = canvas.show_loop(window_name, 1)
                if key in (ord("q"), ord("Q"), 27):
                    break
            await asyncio.sleep(frame_delay)
    finally:
        if ctx.sound is not None:
            ctx.sound.stop_background()
        cv2.destroyWindow(window_name)
        cv2.waitKey(1)


async def run(uri: str):
    username, password = login_prompt()
    bus, _score, _log, sound, _animations = create_event_system(sound_enabled=True)
    ctx = ClientContext(bus=bus, sound=sound)
    inbox: asyncio.Queue = asyncio.Queue()

    print(f"Connecting to {uri} ...")
    async with websockets.connect(uri) as ws:
        ctx.websocket = ws
        await ws.send(encode_message("login", username=username, password=password))

        recv = asyncio.create_task(_receiver(ws, inbox))
        proc = asyncio.create_task(_process_inbox(inbox, ctx))

        while not ctx.logged_in:
            await asyncio.sleep(0.05)
            if ctx.status_line.startswith("Login failed"):
                print(ctx.status_line)
                return

        print(f"Logged in as {username} (ELO {ctx.my_rating})")
        try:
            if await _enter_room(ws, ctx):
                print(
                    f"Game started — Room {ctx.room_id}, "
                    f"you are {ctx.my_role.upper()} on the shared board"
                )
                await _graphics_loop(ctx)
        finally:
            sound.stop_background()
            recv.cancel()
            proc.cancel()
            for t in (recv, proc):
                try:
                    await t
                except asyncio.CancelledError:
                    pass


def main():
    p = argparse.ArgumentParser(description="Kung Fu Chess — play with a friend online")
    p.add_argument(
        "--host",
        default="127.0.0.1",
        help="Server IP (friend uses the host's public/LAN IP)",
    )
    p.add_argument("--port", type=int, default=8765)
    args = p.parse_args()
    asyncio.run(run(f"ws://{args.host}:{args.port}/ws"))


if __name__ == "__main__":
    main()
