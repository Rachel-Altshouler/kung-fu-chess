import sys
from board import ChessBoard

def main():
    # URL: https://github.com/Rachel-Altshouler/kung-fu-chess
    input_lines = sys.stdin.readlines()
    board = ChessBoard()
    success = board.load_from_text_lines(input_lines)
    if not success:
        return
    print(board.get_canonical_representation())

if __name__ == "__main__":
    main()
