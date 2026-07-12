import sys
from game_io.board_parser import BoardParser
from game_io.board_printer import BoardPrinter
from model.constants import Commands


def process_commands(board, commands):
    """מנהלת את הרצת הפקודות על הלוח"""
    for command in commands:
        parts = command.split()
        if not parts:
            continue

        cmd_type = parts[0]

        if cmd_type == Commands.CLICK:
            # המרת הקלט למספרים והפעלה על הלוח
            x, y = int(parts[1]), int(parts[2])
            board.handle_click(x, y)

        elif cmd_type == Commands.WAIT:
            # המרת הזמן והפעלה על הלוח
            ms = int(parts[1])
            board.handle_wait(ms)

        elif command.strip() == Commands.PRINT_BOARD:
            # שימוש במדפסת כדי להציג את מצב הלוח הנוכחי
            print(BoardPrinter.get_canonical_representation(board))


def main():
    # קריאת כל הקלט מה-stdin
    input_lines = sys.stdin.readlines()

    # 1. פירסור הלוח (יצירת אובייקט הלוח הראשוני)
    board = BoardParser.parse_from_lines(input_lines)
    if board is None:
        return

    # 2. הפרדת הפקודות מהקלט
    commands = []
    is_command_section = False
    for line in input_lines:
        line = line.strip()
        if line == "Commands:":
            is_command_section = True
            continue
        if is_command_section and line:
            commands.append(line)

    # 3. הרצת הפקודות
    process_commands(board, commands)


if __name__ == "__main__":
    main()