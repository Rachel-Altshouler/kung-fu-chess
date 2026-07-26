# Kung Fu Chess — play with a friend online

Two players in different places each open the client, join the **same Room ID**,
and play on **one shared board** (server authority over FastAPI + WebSocket).

## Setup

```powershell
cd kung-fu
py -3.9 -m pip install -r requirements.txt
```

Copy `assets/` into `kung-fu/` if pieces/board images are missing.

## Run

### On the host computer (one player hosts the server)

```powershell
py -3.9 server/main.py
```

Server listens on all interfaces (`0.0.0.0:8765`).

### Each player (own computer)

```powershell
# Same PC as server:
py -3.9 client/graphics_main.py

# Friend on another PC — use the host's IP:
py -3.9 client/graphics_main.py --host 192.168.x.x
```

### In each client

1. **Login** with different usernames  
2. One player: **Create room** → copy the **Room ID** shown  
3. Friend: **Join room** → paste that Room ID  
4. When both are in, the shared board opens — play  
   - You move only your color (White / Black)  
   - Left-click move, right-click jump  
   - Soft sound on moves; move history on the sides  

## How it works

```
Player A PC ──WebSocket──┐
                         ├── FastAPI server ── one GameEngine per Room ID
Player B PC ──WebSocket──┘
```

Both windows show the **same** board state from the server.

## Firewall

Allow inbound TCP port **8765** on the host if friends connect over the internet/LAN.
