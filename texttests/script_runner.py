from model.constants import Commands
from view.renderer import Renderer


class ScriptRunner:
    @staticmethod
    def run(game_engine, commands):
        for command in commands:
            parts = command.split()
            if not parts:
                continue

            cmd_type = parts[0]

            if cmd_type == Commands.CLICK:
                x, y = int(parts[1]), int(parts[2])
                game_engine.handle_click(x, y)

            elif cmd_type == Commands.JUMP:
                x, y = int(parts[1]), int(parts[2])
                game_engine.handle_jump(x, y)

            elif cmd_type == Commands.WAIT:
                milliseconds = int(parts[1])
                game_engine.handle_wait(milliseconds)

            elif command.strip() == Commands.PRINT_BOARD:
                print(Renderer.render_text(game_engine.get_board()))
