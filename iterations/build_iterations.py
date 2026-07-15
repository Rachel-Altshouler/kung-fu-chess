"""Build iteration submission folders (iter01 is hand-crafted)."""
from __future__ import annotations

import ast
import os
import shutil
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITER = Path(__file__).resolve().parent
TEMPLATES = ITER / "templates"

CUMULATIVE_TESTS: dict[int, dict[str, set[str] | None]] = {
    2: {
        "test_game_engine.py": {
            "test_handle_click_valid_king_move",
            "test_handle_click_invalid_king_move",
            "test_handle_wait",
            "test_script_runner_click",
            "test_script_runner_wait",
            "test_script_runner_print_board",
            "test_script_runner_empty_line",
            "test_app_valid_input",
            "test_app_invalid_board",
            "test_app_as_script",
        },
        "test_rule_engine.py": {
            "test_are_same_color",
            "test_valid_king_move",
            "test_cannot_capture_friendly_piece",
            "test_are_same_color_with_empty_cell",
            "test_invalid_move_out_of_bounds",
            "test_invalid_move_from_empty_source",
            "test_valid_move_with_position_object",
        },
        "test_board_printer.py": {"test_canonical_representation", "test_empty_board"},
    },
    3: {
        "test_piece_rules.py": {
            "test_is_path_blocked", "test_king_move", "test_rook_move", "test_bishop_move",
            "test_queen_move", "test_knight_move", "test_piece_move_valid_for_each_type",
        },
        "test_game_engine.py": {
            "test_handle_click_valid_knight_move",
        },
    },
    4: {
        "test_piece_rules.py": {"test_knight_jumps_over_blocker"},
        "test_rule_engine.py": {"test_can_capture_enemy_piece"},
        "test_game_engine.py": {
            "test_handle_click_capture_enemy",
            "test_handle_click_valid_knight_move",
        },
    },
    5: {
        "test_piece_rules.py": {
            "test_white_pawn_moves_up", "test_black_pawn_moves_down",
            "test_white_pawn_captures_diagonally", "test_black_pawn_captures_diagonally",
            "test_pawn_cannot_capture_forward", "test_pawn_cannot_move_diagonally_to_empty",
            "test_white_pawn_cannot_move_down", "test_black_pawn_cannot_move_up",
        },
        "test_rule_engine.py": {
            "test_white_pawn_forward_move", "test_black_pawn_forward_move",
            "test_pawn_diagonal_capture", "test_pawn_cannot_capture_forward",
        },
        "test_game_engine.py": {"test_pawn_cannot_capture_forward_during_game"},
    },
    6: {
        "test_piece_rules.py": {
            "test_pawn_two_square_from_start_when_path_clear",
            "test_pawn_two_square_blocked_when_path_not_clear",
            "test_pawn_cannot_move_two_squares_after_leaving_start",
            "test_pawn_cannot_move_two_squares_in_wrong_direction",
        },
        "test_game_engine.py": {
            "test_white_pawn_promotes_to_queen_on_last_row",
            "test_black_pawn_promotes_to_queen_on_last_row",
            "test_pawn_two_square_move_through_engine",
            "test_handle_click_white_pawn_move",
        },
    },
    7: {
        "test_game_engine.py": {
            "test_board_shows_original_position_before_arrival",
            "test_board_shows_destination_after_sufficient_wait",
            "test_print_board_before_and_after_movement",
            "test_board_unchanged_before_move_finishes",
            "test_start_movement_with_position_object",
        },
    },
    8: {
        "test_game_engine.py": {
            "test_cannot_command_while_moving",
            "test_cannot_start_new_move_while_piece_is_moving",
            "test_can_move_again_immediately_after_arrival_without_cooldown",
            "test_consecutive_moves_without_cooldown",
            "test_cannot_command_same_piece_while_it_is_moving",
            "test_try_move_blocked_while_moving",
        },
    },
    9: {
        "test_real_time_arbiter.py": None,
        "test_game_engine.py": {
            "test_two_pieces_can_move_at_the_same_time",
            "test_enemy_collision_later_arrival_captures",
            "test_friendly_crossing_stops_later_piece",
            "test_game_state_clock_and_movements",
            "test_apply_completed_skips_movement_removed_before_resolution",
        },
    },
    10: {
        "test_game_engine.py": {
            "test_capturing_enemy_king_ends_game",
            "test_late_move_commands_ignored_after_game_over",
        },
    },
    11: {
        "test_board_printer.py": {
            "test_renderer_uses_board_printer",
            "test_image_view_not_available_in_text_mode",
        },
        "test_game_engine.py": {
            "test_knight_jump_captures_enemy_arriving_during_flight",
            "test_knight_stays_at_source_cell_during_jump",
            "test_knight_lands_normally_when_no_enemy_arrives_during_jump",
            "test_captured_piece_cannot_jump",
            "test_knight_jump_capture_king_ends_game",
            "test_jump_command_lands_same_square",
            "test_jump_command_captures_arriving_enemy",
            "test_jump_on_friendly_cell_captures_arriving_enemy",
        },
    },
}

BASE_TESTS = [
    "test_board_parser.py",
    "test_position.py",
    "test_board.py",
    "test_board_mapper.py",
    "test_controller.py",
]


def silent_parser_src() -> Path:
    return ITER / "iter01" / "game_io" / "board_parser.py"


def _keep_class_member(item: ast.stmt, allowed: set[str] | None) -> bool:
    if not isinstance(item, ast.FunctionDef):
        return True
    if item.name.startswith("test_"):
        return allowed is None or item.name in allowed
    return item.name in {"setUp", "tearDown", "setUpClass", "tearDownClass"}


def filter_test_file(src: Path, allowed: set[str] | None) -> str:
    module = ast.parse(src.read_text(encoding="utf-8"))
    kept_nodes: list[ast.stmt] = []
    for node in module.body:
        if isinstance(node, ast.ClassDef):
            methods = [item for item in node.body if _keep_class_member(item, allowed)]
            if any(isinstance(m, ast.FunctionDef) and m.name.startswith("test_") for m in methods):
                node.body = methods
                kept_nodes.append(node)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            kept_nodes.append(node)
    new_module = ast.Module(body=kept_nodes, type_ignores=[])
    ast.fix_missing_locations(new_module)
    return ast.unparse(new_module) + "\n"


def cumulative_allowed(iter_num: int, filename: str) -> set[str] | None:
    allowed: set[str] = set()
    use_full = False
    for n in range(2, iter_num + 1):
        spec = CUMULATIVE_TESTS.get(n, {})
        if filename not in spec:
            continue
        file_allowed = spec[filename]
        if file_allowed is None:
            use_full = True
        else:
            allowed |= file_allowed
    if use_full:
        return None
    return allowed if allowed else None


def patch_test_imports(text: str) -> str:
    return text.replace("from app import main", "from main import main").replace(
        "runpy.run_module('app', run_name='__main__')",
        "runpy.run_module('main', run_name='__main__')",
    )


def add_texttests(target: Path):
    dst = target / "texttests"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(TEMPLATES / "texttests", dst)


def copy_tests_for_iter(target: Path, iter_num: int):
    tests_dir = target / "tests" / "unit"
    tests_dir.mkdir(parents=True, exist_ok=True)
    for old in tests_dir.glob("test_*.py"):
        old.unlink()
    (tests_dir / "__init__.py").write_text("", encoding="utf-8")

    if iter_num == 1:
        shutil.copy2(ITER / "iter01" / "tests" / "unit" / "test_iter01.py", tests_dir / "test_iter01.py")
        return

    if iter_num == 11:
        for src in (ROOT / "tests" / "unit").glob("test_*.py"):
            shutil.copy2(src, tests_dir / src.name)
        return

    for name in BASE_TESTS:
        shutil.copy2(ROOT / "tests" / "unit" / name, tests_dir / name)

    extra = ["test_rule_engine.py", "test_piece_rules.py", "test_game_engine.py"]
    if iter_num >= 9:
        extra.append("test_real_time_arbiter.py")

    printer_allowed = cumulative_allowed(iter_num, "test_board_printer.py")
    src = ROOT / "tests" / "unit" / "test_board_printer.py"
    view_tests = {"test_renderer_uses_board_printer", "test_image_view_not_available_in_text_mode"}
    if printer_allowed is None:
        shutil.copy2(src, tests_dir / "test_board_printer.py")
    elif not (printer_allowed & view_tests):
        shutil.copy2(TEMPLATES / "tests" / "test_board_printer.py", tests_dir / "test_board_printer.py")
    else:
        (tests_dir / "test_board_printer.py").write_text(
            filter_test_file(src, printer_allowed), encoding="utf-8"
        )

    for name in extra:
        src = ROOT / "tests" / "unit" / name
        if not src.exists():
            continue
        if name == "test_game_engine.py" and iter_num <= 6:
            src = TEMPLATES / "tests" / "test_game_engine_immediate.py"
        if any(
            CUMULATIVE_TESTS.get(n, {}).get(name) is None
            for n in range(2, iter_num + 1)
            if name in CUMULATIVE_TESTS.get(n, {})
        ):
            content = src.read_text(encoding="utf-8")
            if name == "test_game_engine.py":
                content = patch_test_imports(content)
            (tests_dir / name).write_text(content, encoding="utf-8")
            continue

        merged: set[str] = set()
        for n in range(2, iter_num + 1):
            for method in CUMULATIVE_TESTS.get(n, {}).get(name, set()) or set():
                merged.add(method)
        content = filter_test_file(src, merged)
        if name == "test_game_engine.py":
            content = patch_test_imports(content)
        (tests_dir / name).write_text(content, encoding="utf-8")


def write_main_click(target: Path):
    shutil.copy2(TEMPLATES / "main_click.py", target / "main.py")


def ensure_init_files(target: Path):
    for path in target.rglob("*"):
        if path.is_dir() and not (path / "__init__.py").exists():
            (path / "__init__.py").write_text("", encoding="utf-8")


def copy_tree_overwrite(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target_item = dst / item.name
        if item.is_dir():
            copy_tree_overwrite(item, target_item)
        else:
            shutil.copy2(item, target_item)


def copy_common(target: Path, folders: list[str]):
    for folder in folders:
        copy_tree_overwrite(ROOT / folder, target / folder)


def patch_piece_rules_no_pawn(path: Path):
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "        if piece_type == 'P':\n            return PieceRules.is_pawn_move(grid, source_position, destination_position, color)",
        "        if piece_type == 'P':\n            return False",
    )
    path.write_text(text, encoding="utf-8")


def sync_game_io(target: Path):
    copy_tree_overwrite(ITER / "iter01" / "game_io", target / "game_io")


def build_iter02():
    target = ITER / "iter02"
    if not target.exists():
        shutil.copytree(ITER / "iter01", target)
    sync_game_io(target)
    (target / "model").mkdir(parents=True, exist_ok=True)
    copy_common(target, ["input", "engine", "rules"])
    shutil.copy2(TEMPLATES / "game_engine_immediate.py", target / "engine" / "game_engine.py")
    shutil.copy2(TEMPLATES / "piece_rules_king_only.py", target / "rules" / "piece_rules.py")
    shutil.copy2(ROOT / "model" / "position.py", target / "model" / "position.py")
    shutil.copy2(ROOT / "model" / "piece.py", target / "model" / "piece.py")
    shutil.copy2(ROOT / "model" / "board.py", target / "model" / "board.py")
    shutil.copy2(ROOT / "model" / "constants.py", target / "model" / "constants.py")
    write_main_click(target)
    add_texttests(target)
    tests_dir = target / "tests" / "unit"
    tests_dir.mkdir(parents=True, exist_ok=True)
    for old in tests_dir.glob("test_*.py"):
        old.unlink()
    (tests_dir / "__init__.py").write_text("", encoding="utf-8")
    for name in BASE_TESTS:
        shutil.copy2(ROOT / "tests" / "unit" / name, tests_dir / name)
    shutil.copy2(TEMPLATES / "tests" / "test_board_printer.py", tests_dir / "test_board_printer.py")
    shutil.copy2(TEMPLATES / "tests" / "test_rule_engine_iter02.py", tests_dir / "test_rule_engine.py")
    shutil.copy2(TEMPLATES / "tests" / "test_game_engine_immediate.py", tests_dir / "test_game_engine.py")
    filtered = filter_test_file(
        tests_dir / "test_game_engine.py",
        {
            method
            for n in range(2, 3)
            for method in CUMULATIVE_TESTS.get(n, {}).get("test_game_engine.py", set()) or set()
        },
    )
    (tests_dir / "test_game_engine.py").write_text(filtered, encoding="utf-8")
    stale = tests_dir / "test_piece_rules.py"
    if stale.exists():
        stale.unlink()
    (target / "README.md").write_text("# Iteration 2\n\nClick-to-move (immediate).\n", encoding="utf-8")


def build_iter03_to06(num: int, readme: str, pawn: bool, promotion: bool):
    target = ITER / f"iter{num:02d}"
    source = ITER / "iter02" if num == 3 else ITER / f"iter{num - 1:02d}"
    if not target.exists():
        shutil.copytree(source, target)
    shutil.copy2(ROOT / "rules" / "piece_rules.py", target / "rules" / "piece_rules.py")
    if not pawn:
        patch_piece_rules_no_pawn(target / "rules" / "piece_rules.py")
    engine = TEMPLATES / "game_engine_immediate.py"
    shutil.copy2(engine, target / "engine" / "game_engine.py")
    write_main_click(target)
    add_texttests(target)
    copy_tests_for_iter(target, num)
    (target / "README.md").write_text(readme, encoding="utf-8")


def build_iter07_to10(num: int, readme: str):
    target = ITER / f"iter{num:02d}"
    if not target.exists():
        shutil.copytree(ITER / "iter06", target)
    copy_common(target, ["realtime"])
    shutil.copy2(ROOT / "engine" / "game_engine.py", target / "engine" / "game_engine.py")
    shutil.copy2(ROOT / "model" / "game_state.py", target / "model" / "game_state.py")
    write_main_click(target)
    add_texttests(target)
    copy_tests_for_iter(target, num)
    (target / "README.md").write_text(readme, encoding="utf-8")


def build_iter11():
    target = ITER / "iter11"
    target.mkdir(parents=True, exist_ok=True)
    copy_common(target, [
        "model", "game_io", "input", "engine", "rules", "realtime", "texttests", "view",
    ])
    shutil.copy2(ROOT / "app.py", target / "app.py")
    shutil.copy2(ROOT / "main.py", target / "main.py")
    if (ROOT / ".coveragerc").exists():
        shutil.copy2(ROOT / ".coveragerc", target / ".coveragerc")
    copy_tests_for_iter(target, 11)
    (target / "README.md").write_text("# Iteration 11\n\nFull project.\n", encoding="utf-8")


def patch_all_parsers():
    parser = silent_parser_src()
    for n in range(1, 12):
        dst = ITER / f"iter{n:02d}" / "game_io" / "board_parser.py"
        if dst.exists() and dst.resolve() != parser.resolve():
            shutil.copy2(parser, dst)


if __name__ == "__main__":
    os.chdir(ROOT)
    build_iter02()
    build_iter03_to06(3, "# Iteration 3\n\nK/R/B/Q/N rules.\n", pawn=False, promotion=False)
    build_iter03_to06(4, "# Iteration 4\n\nBlocking + capture.\n", pawn=False, promotion=False)
    build_iter03_to06(5, "# Iteration 5\n\nBasic pawn rules.\n", pawn=True, promotion=False)
    build_iter03_to06(6, "# Iteration 6\n\nTwo-square pawn + promotion.\n", pawn=True, promotion=True)
    build_iter07_to10(7, "# Iteration 7\n\nTimed movement.\n")
    build_iter07_to10(8, "# Iteration 8\n\nNo move while moving.\n")
    build_iter07_to10(9, "# Iteration 9\n\nCollisions.\n")
    build_iter07_to10(10, "# Iteration 10\n\nGame over.\n")
    build_iter11()
    patch_all_parsers()
    for n in range(1, 12):
        target = ITER / f"iter{n:02d}"
        if n >= 2:
            sync_game_io(target)
        ensure_init_files(target)
    (ITER / "iter01" / "README.md").write_text(
        "# Iteration 1\n\nBoard parsing, validation, canonical print.\n", encoding="utf-8"
    )
    print("Built iter01-iter11")
