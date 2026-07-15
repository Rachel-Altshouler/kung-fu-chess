import sys

from game_io.board_parser import BoardParser
from game_io.board_printer import BoardPrinter
from model.constants import InputHeaders


def parse_commands(lines):
    commands = []
    in_commands = False
    for line in lines:
        line = line.strip()
        if line == InputHeaders.COMMANDS_HEADER:
            in_commands = True
            continue
        if in_commands and line:
            commands.append(line)
    return commands


def process_commands(board, commands):
    for command in commands:
        command = command.strip()
        if not command:
            continue
        if command == "print board":
            print(BoardPrinter.get_canonical_representation(board))


def main():
    lines = sys.stdin.readlines()
    board = BoardParser.parse_from_lines(lines)
    if board is None:
        return
    process_commands(board, parse_commands(lines))


if __name__ == "__main__":
    main()
