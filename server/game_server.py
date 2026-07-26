from __future__ import annotations

import asyncio
import secrets
import traceback
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from fastapi import WebSocket, WebSocketDisconnect

from domain.board import ChessBoard
from domain.constants import BoardConstants, GraphicsConstants
from engine.game_engine import GameEngine
from server.command_parser import parse_compact_command
from server.elo import pair_result_scores, update_elo
from server.logging_util import log_event, setup_logger
from server.protocol import decode_message, encode_message, snapshot_to_dict
from server.squares import square_to_coords
from server.user_db import UserDatabase


@dataclass
class ConnectedUser:
    websocket: WebSocket
    username: str
    rating: int
    room_id: str | None = None


@dataclass
class RoomPlayer:
    websocket: WebSocket
    username: str
    role: str
    rating: int


@dataclass
class GameRoom:
    room_id: str
    engine: GameEngine
    players: list[RoomPlayer] = field(default_factory=list)
    elo_applied: bool = False
    game_started_sent: bool = False

    def sockets(self):
        for p in self.players:
            yield p.websocket

    def player_for(self, websocket: WebSocket) -> RoomPlayer | None:
        for p in self.players:
            if p.websocket is websocket:
                return p
        return None

    def players_public(self):
        return [
            {"username": p.username, "role": p.role, "rating": p.rating}
            for p in self.players
        ]

    def by_role(self, role: str) -> RoomPlayer | None:
        for p in self.players:
            if p.role == role:
                return p
        return None


class GameServer:
    """
    FastAPI WebSocket server: friends create/join a Room ID.
    Each room has ONE shared GameEngine — both clients sync to that board.
    """

    def __init__(self, db_path: str | Path | None = None):
        self.user_db = UserDatabase(db_path)
        self.logger = setup_logger(
            "server", Path(__file__).resolve().parent / "logs"
        )
        self.clients: dict[WebSocket, ConnectedUser] = {}
        self.rooms: dict[str, GameRoom] = {}
        self._lock = asyncio.Lock()

    async def run_tick_loop(self):
        delay = GraphicsConstants.FRAME_DELAY_MS / 1000.0
        while True:
            updates: list[tuple[GameRoom, str, dict | None]] = []
            async with self._lock:
                for room in list(self.rooms.values()):
                    if len(room.players) >= 2 and not room.engine.is_game_over():
                        room.engine.handle_wait(GraphicsConstants.FRAME_DELAY_MS)
                    elo = self._apply_elo_if_needed(room)
                    if room.players:
                        updates.append((room, self._room_state(room), elo))
            for room, state, elo in updates:
                targets = set(room.sockets())
                await self._broadcast(state, only=targets)
                if elo is not None:
                    await self._broadcast(
                        encode_message("elo_updated", **elo),
                        only=targets,
                    )
            await asyncio.sleep(delay)

    async def handle_connection(self, websocket: WebSocket):
        await websocket.accept()
        log_event(self.logger, "client_connected")
        try:
            await websocket.send_text(
                encode_message(
                    "hello",
                    message="Login, then Create or Join a room to play with a friend.",
                )
            )
            while True:
                raw = await websocket.receive_text()
                response = await self._handle_raw_message(raw, websocket)
                if response is not None:
                    await websocket.send_text(response)
        except WebSocketDisconnect:
            log_event(self.logger, "client_disconnected")
        finally:
            await self._cleanup_connection(websocket)

    async def _cleanup_connection(self, websocket: WebSocket):
        user = self.clients.pop(websocket, None)
        if user is None or user.room_id is None:
            return
        room = self.rooms.get(user.room_id)
        if room is None:
            return
        removed = room.player_for(websocket)
        room.players = [p for p in room.players if p.websocket is not websocket]
        user.room_id = None
        if removed:
            log_event(
                self.logger,
                "player_left",
                room_id=room.room_id,
                username=removed.username,
            )
            room.game_started_sent = False
            await self._broadcast(
                encode_message(
                    "player_left",
                    username=removed.username,
                    role=removed.role,
                    room_id=room.room_id,
                    players=room.players_public(),
                ),
                only=set(room.sockets()),
            )
        if not room.players:
            self.rooms.pop(room.room_id, None)
            log_event(self.logger, "room_closed", room_id=room.room_id)

    async def _handle_raw_message(self, raw: str, websocket: WebSocket) -> str | None:
        try:
            if raw.strip().startswith("{"):
                message = decode_message(raw)
            else:
                message = {"type": "command", "command": raw.strip()}
            return await self._handle_message(message, websocket)
        except Exception as exc:
            traceback.print_exc()
            log_event(self.logger, "error", detail=str(exc))
            return encode_message("error", message=str(exc))

    async def _handle_message(self, message: dict, websocket: WebSocket) -> str | None:
        message_type = message.get("type", "").lower()
        log_event(self.logger, "message_in", type=message_type)

        if message_type == "login":
            return await self._handle_login(message, websocket)
        if message_type == "create_room":
            return await self._handle_create_room(websocket)
        if message_type == "join_room":
            return await self._handle_join_room(message, websocket)
        if message_type in ("command", "move", "jump", "wait", "state", "get_state"):
            return await self._handle_game_message(message, websocket, message_type)
        if message_type in ("find_match", "cancel_match"):
            return encode_message(
                "error",
                message="Use Create Room / Join Room to play with a friend.",
            )
        return encode_message("error", message=f"Unknown message type: {message_type}")

    async def _handle_login(self, message: dict, websocket: WebSocket) -> str:
        username = (message.get("username") or "").strip()
        password = message.get("password") or ""
        if not username or not password:
            return encode_message("login_denied", detail="username and password required")

        auth = self.user_db.authenticate_or_register(username, password)
        if not auth["ok"]:
            return encode_message("login_denied", detail=auth["detail"])

        # Same username already connected elsewhere?
        for other in self.clients.values():
            if other.username == auth["username"] and other.websocket is not websocket:
                return encode_message(
                    "login_denied",
                    detail="This username is already connected.",
                )

        self.clients[websocket] = ConnectedUser(
            websocket=websocket,
            username=auth["username"],
            rating=auth["rating"],
        )
        log_event(
            self.logger,
            "login_ok",
            username=auth["username"],
            rating=auth["rating"],
        )
        return encode_message(
            "login_ok",
            username=auth["username"],
            rating=auth["rating"],
            created=bool(auth.get("created")),
        )

    async def _handle_create_room(self, websocket: WebSocket) -> str:
        user = self.clients.get(websocket)
        if user is None:
            return encode_message("error", message="login required")
        if user.room_id is not None:
            return encode_message("error", message="already in a room")

        room_id = secrets.token_hex(3).upper()
        room = GameRoom(
            room_id=room_id,
            engine=GameEngine(ChessBoard.create_standard_setup()),
        )
        room.players.append(
            RoomPlayer(websocket, user.username, "white", user.rating)
        )
        user.room_id = room_id
        self.rooms[room_id] = room
        log_event(self.logger, "room_created", room_id=room_id, host=user.username)
        return encode_message(
            "room_created",
            room_id=room_id,
            role="white",
            state=snapshot_to_dict(room.engine.get_snapshot()),
            players=room.players_public(),
            waiting=True,
            detail=f"Share Room ID {room_id} with your friend.",
        )

    async def _handle_join_room(self, message: dict, websocket: WebSocket) -> str | None:
        user = self.clients.get(websocket)
        if user is None:
            return encode_message("error", message="login required")

        room_id = (message.get("room_id") or "").strip().upper()
        room = self.rooms.get(room_id)
        if room is None:
            return encode_message("error", message="room not found — check the Room ID")

        if user.room_id is not None and user.room_id != room_id:
            return encode_message("error", message="already in another room")

        existing = room.player_for(websocket)
        if existing is not None:
            return encode_message(
                "room_joined",
                room_id=room_id,
                role=existing.role,
                state=snapshot_to_dict(room.engine.get_snapshot()),
                players=room.players_public(),
                waiting=len(room.players) < 2,
            )

        if len(room.players) >= 2:
            return encode_message("error", message="room is full (2 players only)")

        # Fill missing color
        taken = {p.role for p in room.players}
        role = "black" if "black" not in taken else "white"
        room.players.append(
            RoomPlayer(websocket, user.username, role, user.rating)
        )
        user.room_id = room_id
        log_event(
            self.logger,
            "room_joined",
            room_id=room_id,
            username=user.username,
            role=role,
        )

        await self._broadcast(
            encode_message(
                "player_joined",
                username=user.username,
                role=role,
                rating=user.rating,
                room_id=room_id,
                players=room.players_public(),
            ),
            only=set(room.sockets()),
        )

        if len(room.players) >= 2:
            await self._announce_game_started(room)
            return None

        return encode_message(
            "room_joined",
            room_id=room_id,
            role=role,
            state=snapshot_to_dict(room.engine.get_snapshot()),
            players=room.players_public(),
            waiting=True,
        )

    async def _announce_game_started(self, room: GameRoom):
        if room.game_started_sent or len(room.players) < 2:
            return
        room.game_started_sent = True
        white = room.by_role("white")
        black = room.by_role("black")
        if white is None or black is None:
            return

        state = snapshot_to_dict(room.engine.get_snapshot())
        players = room.players_public()
        log_event(
            self.logger,
            "game_started",
            room_id=room.room_id,
            white=white.username,
            black=black.username,
        )
        for player, opponent in ((white, black), (black, white)):
            msg = encode_message(
                "game_started",
                room_id=room.room_id,
                role=player.role,
                opponent=opponent.username,
                opponent_rating=opponent.rating,
                rating=player.rating,
                state=state,
                players=players,
            )
            await self._send_safe(player.websocket, msg)

    def _room_for(self, websocket: WebSocket) -> GameRoom | None:
        user = self.clients.get(websocket)
        if user is None or user.room_id is None:
            return None
        return self.rooms.get(user.room_id)

    async def _handle_game_message(
        self, message: dict, websocket: WebSocket, message_type: str
    ) -> str | None:
        room = self._room_for(websocket)
        if room is None:
            return encode_message("error", message="join a room first")

        player = room.player_for(websocket)
        if player is None:
            return encode_message("error", message="not in room")

        if message_type in ("command", "move", "jump"):
            if len(room.players) < 2:
                return encode_message(
                    "ack", ok=False, detail="waiting for your friend to join the room"
                )
            async with self._lock:
                if message_type == "jump":
                    result = self._apply_jump(message, room, player)
                else:
                    result = self._apply_command(message, room, player)
                state = self._room_state(room)
            await self._broadcast(state, only=set(room.sockets()))
            return encode_message("ack", **result)

        if message_type in ("wait", "state", "get_state"):
            async with self._lock:
                return self._room_state(room)

        return encode_message("error", message="unknown game message")

    def _piece_owned_by_player(self, token: str, role: str) -> bool:
        if not token or token == BoardConstants.EMPTY_CELL:
            return False
        color = token[0].upper()
        if role == "white":
            return color == "W"
        if role == "black":
            return color == "B"
        return False

    def _apply_command(self, message: dict, room: GameRoom, player: RoomPlayer) -> dict:
        if room.engine.is_game_over():
            return {"ok": False, "detail": "game is over"}
        command_text = message.get("command") or message.get("token")
        if command_text:
            parsed = parse_compact_command(command_text)
        else:
            board_rows = len(room.engine.get_board().get_grid())
            source = message.get("source")
            destination = message.get("destination")
            if isinstance(source, str):
                source = square_to_coords(source, board_rows)
            if isinstance(destination, str):
                destination = square_to_coords(destination, board_rows)
            if source is None or destination is None:
                return {"ok": False, "detail": "source and destination required"}
            parsed = {
                "source": tuple(source),
                "destination": tuple(destination),
                "token": message.get("token"),
            }

        board = room.engine.get_board()
        source = parsed["source"]
        destination = parsed["destination"]
        actual_token = board.get_piece_at(source)
        if actual_token == BoardConstants.EMPTY_CELL:
            return {"ok": False, "detail": "source square is empty"}
        if not self._piece_owned_by_player(actual_token, player.role):
            return {
                "ok": False,
                "detail": f"you are {player.role} — move your own pieces only",
            }
        ok = room.engine.try_move(source, destination)
        return {"ok": ok, "detail": "move started" if ok else "illegal move"}

    def _apply_jump(self, message: dict, room: GameRoom, player: RoomPlayer) -> dict:
        if room.engine.is_game_over():
            return {"ok": False, "detail": "game is over"}
        command_text = message.get("command")
        board_rows = len(room.engine.get_board().get_grid())
        if command_text:
            parsed = parse_compact_command(command_text, board_rows)
            source = parsed["source"]
        else:
            source = message.get("source")
            if isinstance(source, str):
                source = square_to_coords(source, board_rows)
            if source is None:
                return {"ok": False, "detail": "source required"}
            source = tuple(source)

        board = room.engine.get_board()
        actual_token = board.get_piece_at(source)
        if actual_token == BoardConstants.EMPTY_CELL:
            return {"ok": False, "detail": "source square is empty"}
        if not self._piece_owned_by_player(actual_token, player.role):
            return {
                "ok": False,
                "detail": f"you are {player.role} — jump your own pieces only",
            }

        cell = BoardConstants.CELL_SIZE
        pixel_x = source[1] * cell + cell // 2
        pixel_y = source[0] * cell + cell // 2
        before = len(room.engine.get_active_movements())
        room.engine.handle_jump(pixel_x, pixel_y)
        after = len(room.engine.get_active_movements())
        ok = after > before
        return {"ok": ok, "detail": "jump started" if ok else "illegal jump"}

    def _apply_elo_if_needed(self, room: GameRoom) -> dict | None:
        if room.elo_applied or not room.engine.is_game_over():
            return None
        if len(room.players) < 2:
            return None
        white = room.by_role("white")
        black = room.by_role("black")
        if white is None or black is None:
            return None
        white_score, black_score = pair_result_scores(
            room.engine.get_winner(),
            room.engine.is_stalemate(),
        )
        old_w, old_b = int(white.rating), int(black.rating)
        new_w = update_elo(old_w, old_b, white_score)
        new_b = update_elo(old_b, old_w, black_score)
        self.user_db.set_rating(white.username, new_w)
        self.user_db.set_rating(black.username, new_b)
        white.rating, black.rating = new_w, new_b
        room.elo_applied = True
        return {
            "white": {
                "username": white.username,
                "old_rating": old_w,
                "new_rating": new_w,
            },
            "black": {
                "username": black.username,
                "old_rating": old_b,
                "new_rating": new_b,
            },
            "is_stalemate": room.engine.is_stalemate(),
            "winner": room.engine.get_winner(),
        }

    def _room_state(self, room: GameRoom) -> str:
        return encode_message(
            "state",
            room_id=room.room_id,
            state=snapshot_to_dict(room.engine.get_snapshot()),
            players=room.players_public(),
        )

    async def _broadcast(self, message: str, only=None):
        stale = []
        for client in list(only or []):
            try:
                await client.send_text(message)
            except (WebSocketDisconnect, RuntimeError):
                stale.append(client)
        for client in stale:
            await self._cleanup_connection(client)

    async def _send_safe(self, websocket: WebSocket, message: str):
        try:
            await websocket.send_text(message)
        except (WebSocketDisconnect, RuntimeError):
            await self._cleanup_connection(websocket)
