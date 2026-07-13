import sys
from engine.game_engine import GameEngine
from texttests.script_parser import ScriptParser
from texttests.script_runner import ScriptRunner


def main():
    input_lines = sys.stdin.readlines()

    board = ScriptParser.parse_board(input_lines)
    if board is None:
        return

    game_engine = GameEngine(board)
    commands = ScriptParser.parse_commands(input_lines)
    ScriptRunner.run(game_engine, commands)


if __name__ == "__main__":
    main()
