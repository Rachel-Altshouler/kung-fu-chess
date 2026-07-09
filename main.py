import sys
from board import ChessBoard
# URL: https://github.com/Rachel-Altshouler/kung-fu-chess

def main():
    board = ChessBoard()

    input_lines = sys.stdin.readlines()

    if not board.load_from_text_lines(input_lines):
        return
    board.process_commands(input_lines)

if __name__ == "__main__":
    main()