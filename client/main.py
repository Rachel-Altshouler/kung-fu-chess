from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

import websockets

KUNG_FU_ROOT = Path(__file__).resolve().parent.parent
if str(KUNG_FU_ROOT) not in sys.path:
    sys.path.insert(0, str(KUNG_FU_ROOT))

import bootstrap  # noqa: F401

from client.home_screen import home_menu, login_prompt
from client.logging_util import setup_client_logger
from server.protocol import decode_message, encode_message

logger = setup_client_logger()


def _log(msg: str):
    logger.info(msg)


def _print_state(state: dict):
    board = state.get("board") or []
    print("\n=== GAME STATE ===")
    if state.get("room_id"):
        print(f"Room: {state.get('room_id')}")
    print(
        f"clock={state.get('clock')}  W={state.get('white_score')}  "
        f"B={state.get('black_score')}  over={state.get('game_over')}"
    )
    for row in board:
        print(" ".join(f"{cell:>2}" for cell in row))
    print("==================\n")


async def run_client(uri: str):
    username, password = login_prompt()
    _log(f"connecting uri={uri} user={username}")

    async with websockets.connect(uri) as websocket:
        await websocket.send(
            encode_message("login", username=username, password=password)
        )

        logged_in = False
        my_role = None
        my_rating = None
        room_id = None
        in_game = False
        game_ready = asyncio.Event()

        async def receiver():
            nonlocal logged_in, my_role, my_rating, room_id, in_game
            async for raw in websocket:
                message = decode_message(raw)
                mtype = message.get("type")
                _log(f"recv type={mtype} body={json.dumps(message)[:200]}")

                if mtype == "hello":
                    print(message.get("message"))
                elif mtype == "login_ok":
                    logged_in = True
                    my_role = message.get("role")
                    my_rating = message.get("rating")
                    waiting = message.get("waiting")
                    print(
                        f"Logged in as {message.get('username')} "
                        f"— {my_role} (ELO {my_rating})"
                    )
                    if waiting:
                        print("Waiting for opponent on the shared board...")
                    elif message.get("state"):
                        in_game = True
                        _print_state(message.get("state") or {})
                        game_ready.set()
                elif mtype == "login_denied":
                    print(f"Login failed: {message.get('detail')}")
                elif mtype == "match_waiting":
                    print(message.get("detail"))
                elif mtype == "match_failed":
                    print(f"** {message.get('detail')} **")
                    in_game = False
                elif mtype == "match_found":
                    in_game = True
                    my_role = message.get("role")
                    my_rating = message.get("rating", my_rating)
                    print(
                        f"Match found! You are {my_role.upper()} vs "
                        f"{message.get('opponent')} "
                        f"(ELO {message.get('opponent_rating')})"
                    )
                    _print_state(message.get("state") or {})
                    game_ready.set()
                elif mtype == "room_created":
                    in_game = True
                    room_id = message.get("room_id")
                    my_role = message.get("role")
                    print(f"Room created: {room_id} — you are {my_role.upper()}")
                    print(f"[Room ID on screen: {room_id}]")
                    _print_state(message.get("state") or {})
                    game_ready.set()
                elif mtype == "room_joined":
                    in_game = True
                    room_id = message.get("room_id")
                    my_role = message.get("role")
                    print(
                        f"Joined room {room_id} as {my_role.upper()}"
                    )
                    print(f"[Room ID on screen: {room_id}]")
                    _print_state(message.get("state") or {})
                    game_ready.set()
                elif mtype == "player_joined":
                    print(
                        f"Player joined: {message.get('username')} "
                        f"as {message.get('role')}"
                    )
                elif mtype == "disconnect_countdown":
                    print(
                        f"\r>>> Opponent ({message.get('role')}) disconnected — "
                        f"resign in {message.get('seconds')}s <<<",
                        end="",
                        flush=True,
                    )
                elif mtype == "opponent_resigned":
                    print(
                        f"\n>>> {message.get('reason')} — "
                        f"winner: {message.get('winner')} <<<"
                    )
                elif mtype == "state":
                    if message.get("room_id"):
                        room_id = message.get("room_id")
                        print(f"[Room ID: {room_id}]")
                    _print_state(message.get("state") or {})
                elif mtype == "ack":
                    status = "OK" if message.get("ok") else "FAIL"
                    print(f"<< ack {status}: {message.get('detail')}")
                elif mtype == "elo_updated":
                    print("ELO updated:", message)
                elif mtype == "error":
                    print(f"ERROR: {message.get('message')}")
                else:
                    print(f"<< {message}")

        recv_task = asyncio.create_task(receiver())

        while not logged_in:
            await asyncio.sleep(0.1)

        try:
            while True:
                choice = home_menu(logged_in=True)
                if choice == "1":
                    if not in_game:
                        game_ready.clear()
                        _log("send find_match")
                        await websocket.send(encode_message("find_match"))
                        try:
                            await asyncio.wait_for(game_ready.wait(), timeout=120)
                        except asyncio.TimeoutError:
                            print("Timed out waiting for opponent.")
                    if in_game:
                        await _game_loop(
                            websocket, my_role, my_rating, room_id
                        )
                elif choice == "2":
                    break
        finally:
            recv_task.cancel()
            try:
                await recv_task
            except asyncio.CancelledError:
                pass


async def _game_loop(websocket, my_role, my_rating, room_id):
    print("In game. Commands: WPe2e4 | jump WKe1e1 | state | quit")
    if room_id:
        print(f"[Room ID: {room_id}]")
    while True:
        prompt = f"[{my_role}|ELO {my_rating}]> "
        line = await asyncio.to_thread(input, prompt)
        text = line.strip()
        if not text:
            continue
        if text.lower() in ("quit", "exit", "q"):
            break
        _log(f"send command text={text}")
        lower = text.lower()
        if lower == "state":
            await websocket.send(encode_message("state"))
        elif lower.startswith("wait"):
            parts = text.split()
            ms = int(parts[1]) if len(parts) > 1 else 100
            await websocket.send(encode_message("wait", ms=ms))
        elif lower.startswith("jump"):
            cmd = text.split(maxsplit=1)[1] if " " in text else ""
            await websocket.send(encode_message("jump", command=cmd))
        else:
            await websocket.send(encode_message("command", command=text))


def main():
    parser = argparse.ArgumentParser(description="Kung Fu Chess client")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    uri = f"ws://{args.host}:{args.port}/ws"
    asyncio.run(run_client(uri))


if __name__ == "__main__":
    main()
