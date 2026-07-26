from __future__ import annotations

import argparse
import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket

KUNG_FU_ROOT = Path(__file__).resolve().parent.parent
if str(KUNG_FU_ROOT) not in sys.path:
    sys.path.insert(0, str(KUNG_FU_ROOT))

import bootstrap  # noqa: F401

from server.game_server import GameServer  # noqa: E402

DEFAULT_DB = Path(__file__).resolve().parent / "game_data.db"
game_server: GameServer | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global game_server
    if game_server is None:
        game_server = GameServer(db_path=DEFAULT_DB)
    tick_task = asyncio.create_task(game_server.run_tick_loop())
    print("Kung Fu Chess server (FastAPI + WebSocket)")
    print("Friends: Create Room / Join Room — one shared board per Room ID")
    print("Listening for clients on /ws")
    yield
    tick_task.cancel()
    try:
        await tick_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="Kung Fu Chess", lifespan=lifespan)


@app.get("/")
async def health():
    return {"status": "ok", "websocket": "/ws"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    assert game_server is not None
    await game_server.handle_connection(websocket)


def main():
    global game_server
    parser = argparse.ArgumentParser(description="Kung Fu Chess server")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="0.0.0.0 = accept connections from other computers",
    )
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", default=str(DEFAULT_DB))
    args = parser.parse_args()
    game_server = GameServer(db_path=args.db)
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
