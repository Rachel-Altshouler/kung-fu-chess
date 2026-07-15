from game_io.board_parser import BoardParser


class ScriptParser:
    @staticmethod
    def parse_board(lines):
        return BoardParser.parse_from_lines(lines)

    @staticmethod
    def parse_commands(lines):
        commands = []
        is_command_section = False
        for line in lines:
            line = line.strip()
            if line == "Commands:":
                is_command_section = True
                continue
            if is_command_section and line:
                commands.append(line)
        return commands
