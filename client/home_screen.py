from __future__ import annotations


def _read_password() -> str:
    print("Password (visible while typing): ", end="", flush=True)
    return input()


def login_prompt() -> tuple[str, str]:
    print()
    print("=================================")
    print("   Kung Fu Chess — Login")
    print("=================================")
    print("New users register automatically (ELO 1200).")
    print()
    while True:
        username = input("Username: ").strip()
        if not username:
            print("Username cannot be empty.")
            continue
        password = _read_password().strip()
        if not password:
            print("Password cannot be empty.")
            continue
        return username, password


def room_prompt() -> tuple[str, str]:
    """
    Return (action, room_id).
    action: create | join | quit
    """
    print()
    print("=================================")
    print("   Play with a friend — Room")
    print("=================================")
    print("1) Create room  — you get a Room ID to send your friend")
    print("2) Join room    — enter the Room ID your friend shared")
    print("3) Quit")
    choice = input("Choose [1/2/3]: ").strip()
    if choice == "1":
        return "create", ""
    if choice == "2":
        room_id = input("Room ID: ").strip().upper()
        if not room_id:
            print("Room ID cannot be empty.")
            return "quit", ""
        return "join", room_id
    return "quit", ""


def home_menu(logged_in: bool) -> str:
    print()
    print("=================================")
    print("   Kung Fu Chess — Home")
    print("=================================")
    if not logged_in:
        print("1) Login")
        print("2) Quit")
        return input("Choose [1/2]: ").strip()
    print("1) Room — create or join")
    print("2) Quit")
    return input("Choose [1/2]: ").strip()


def room_menu() -> tuple[str, str]:
    """Compatibility wrapper used by text client."""
    action, room_id = room_prompt()
    if action == "quit":
        return "cancel", ""
    return action, room_id
